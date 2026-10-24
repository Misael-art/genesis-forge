#!/usr/bin/env python3
"""Private working-tree transfer. Hash-bound files, no credentials or host state.

Git is provenance, not the content inventory: selected untracked/ignored files
are included. Restore always creates a NEW destination, never overlays a clone.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from bootstrap_host import digest, local_path, publish_new, write_json

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ssh", ".gnupg", ".ai-memory", "graphify-out", "node_modules"}
SKIP_FILES = {".env", "session.json", "xauth", "ctl.sock", "credentials", "credentials.json"}
BRIDGES = {".agent", ".agents", ".trae", ".claude", ".cursor", ".serena", ".superpowers"}


def sensitive(relative):
    return any(p in SKIP_FILES or p.startswith(".env.") or PurePosixPath(p).suffix in (".pem", ".key") for p in relative.parts)


def excluded(relative):
    return any(p in SKIP_DIRS or p == "out" or p.startswith("out.broken") for p in relative.parts) or sensitive(relative) or relative.suffix in (".pyc", ".so")


def inventory(repo, scopes):
    entries = {}
    skipped = []
    total_bytes = 0
    for scope in scopes:
        scope_path = PurePosixPath(scope)
        if any(p in SKIP_DIRS or p == "host_tools" for p in scope_path.parts) or sensitive(scope_path) or scope_path.suffix in (".so", ".pyc"):
            raise ValueError(f"forbidden_scope:{scope}")
        src = local_path(repo, scope)
        if not src.exists():
            raise ValueError(f"required_scope_missing:{scope}")
        # Explicit out/... scopes intentionally preserve selected evidence.
        def collect(path, suffix, ancestors=frozenset()):
            nonlocal total_bytes
            rel = path.relative_to(repo).as_posix()
            if sensitive(PurePosixPath(rel)):
                skipped.append(rel); return
            if path.name in BRIDGES and not rel.startswith("tools/sgdk_wrapper/.agent") and (path.name != ".agent" or path.is_symlink()):
                skipped.append(rel); return
            if suffix.parts and excluded(suffix):
                skipped.append(rel); return
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(repo):
                raise ValueError(f"external_symlink:{rel}")
            resolved_rel = resolved.relative_to(repo)
            if sensitive(resolved_rel) or any(p in SKIP_DIRS for p in resolved_rel.parts):
                raise ValueError(f"sensitive_symlink_target:{rel}")
            if path.is_symlink():
                resolved = path.resolve(strict=True)
                if not resolved.is_relative_to(repo):
                    raise ValueError(f"external_symlink:{rel}")
                if sensitive(resolved.relative_to(repo)) or any(p in SKIP_DIRS for p in resolved.relative_to(repo).parts):
                    raise ValueError(f"sensitive_symlink_target:{rel}")
                # Materialize internal aliases; restore has no symlink pivot.
            if path.is_file():
                size = path.stat().st_size
                previous_size = entries.get(rel, {}).get("size", 0)
                if (len(entries) >= 200000 and rel not in entries) or total_bytes - previous_size + size > 32 * 1024**3:
                    raise ValueError("inventory_budget_exceeded_split_transfer_into_smaller_scopes")
                total_bytes += size - previous_size
                entries[rel] = {"path": rel, "size": size, "sha256": digest(path), "executable": bool(path.stat().st_mode & 0o111)}
                if len(entries) % 5000 == 0:
                    print(f"transfer_inventory_files={len(entries)} bytes={total_bytes}", file=__import__("sys").stderr, flush=True)
            elif path.is_dir():
                if (path / "pyvenv.cfg").is_file():
                    skipped.append(rel + " [virtualenv_recreate_at_destination]"); return
                resolved = path.resolve()
                if resolved in ancestors:
                    raise ValueError(f"directory_alias_cycle:{rel}")
                for child in sorted(path.iterdir()):
                    collect(child, suffix / child.name, ancestors | {resolved})
            else:
                raise ValueError(f"special_file_not_transferable:{rel}")
        collect(src, Path())
    if not entries:
        raise ValueError("empty_transfer")
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
    return {"schema": "forge_host_transfer.v1", "private": True, "scopes": scopes,
            "source_git_head": head.stdout.strip() if head.returncode == 0 else None,
            "git_metadata_included": False, "host_installations_included": False,
            "files": sorted(entries.values(), key=lambda x: x["path"]), "skipped": skipped,
            "total_bytes": sum(x["size"] for x in entries.values()),
            "claim_ceiling": "byte_identity_only_no_new_game_qa"}


class HashReader:
    def __init__(self, stream):
        self.stream = stream
        self.hash = hashlib.sha256()

    def read(self, size=-1):
        data = self.stream.read(size)
        self.hash.update(data)
        return data


def create(repo, scopes, output):
    output = local_path(repo, output)
    if not output.relative_to(repo).parts[0] == "out":
        raise ValueError("transfer_archive_must_live_under_workspace_out")
    if output.exists():
        raise ValueError("transfer_destination_exists_never_overwrite")
    manifest = inventory(repo, scopes)
    output.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(output.parent).free < manifest["total_bytes"] + 64 * 1024**2:
        raise ValueError("insufficient_disk_for_private_transfer")
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".partial", delete=False) as tmp:
        temporary = Path(tmp.name)
    try:
        with tarfile.open(temporary, "w") as tf:
            for entry in manifest["files"]:
                path = repo / entry["path"]
                info = tarfile.TarInfo("payload/" + entry["path"])
                info.size = entry["size"]
                info.mode = 0o755 if entry["executable"] else 0o644
                with path.open("rb") as src:
                    reader = HashReader(src)
                    tf.addfile(info, reader)
                    # A concurrent writer cannot silently contaminate the copy.
                    if reader.hash.hexdigest() != entry["sha256"] or src.read(1):
                        raise ValueError(f"source_changed_during_export:{entry['path']}")
            raw = (json.dumps(manifest, indent=2) + "\n").encode()
            info = tarfile.TarInfo("manifest.json"); info.size = len(raw); info.mode = 0o600
            tf.addfile(info, io.BytesIO(raw))
        temporary.chmod(0o600)
        publish_new(temporary, output)
        receipt = {"archive": output.relative_to(repo).as_posix(), "sha256": digest(output), "files": len(manifest["files"]), "payload_bytes": manifest["total_bytes"], "private": True}
        write_json(output.with_suffix(output.suffix + ".json"), receipt)
        return receipt
    finally:
        temporary.unlink(missing_ok=True)


def validate_archive(tf):
    members = []
    for member in tf:
        if len(members) >= 300000 or not member.isfile():
            raise ValueError("archive_requires_bounded_regular_files_only")
        members.append(member)
    names = [m.name for m in members]
    by_name = {m.name: m for m in members}
    if len(set(names)) != len(names) or names.count("manifest.json") != 1:
        raise ValueError("duplicate_or_missing_archive_member")
    meta = by_name["manifest.json"]
    if meta.size > 32 * 1024**2:
        raise ValueError("manifest_too_large")
    if isinstance(tf.fileobj, BoundedMetadata):
        tf.fileobj.metadata_phase = False
    manifest = json.load(tf.extractfile(meta))
    if manifest.get("schema") != "forge_host_transfer.v1" or manifest.get("private") is not True:
        raise ValueError("unexpected_transfer_schema")
    entries = manifest["files"]
    if not isinstance(entries, list) or not entries or len(entries) > 200000:
        raise ValueError("invalid_transfer_file_inventory")
    expected = {"manifest.json"}
    seen = set()
    for entry in entries:
        rel = entry["path"]
        # Validate on a synthetic root before ANY destination mutation.
        local_path(Path("/forge_transfer_validation"), rel)
        if rel in seen or rel in ("doc/host_transfer_manifest.json", "out/logs/host_transfer_restore_report.json"):
            raise ValueError("duplicate_or_reserved_payload_path")
        if not isinstance(entry["size"], int) or entry["size"] < 0 or len(entry["sha256"]) != 64:
            raise ValueError("invalid_manifest_entry")
        seen.add(rel)
        name = "payload/" + rel
        expected.add(name)
        if name not in by_name or by_name[name].size != entry["size"]:
            raise ValueError(f"payload_size_or_member_mismatch:{rel}")
    if set(names) != expected or sum(e["size"] for e in entries) != manifest["total_bytes"]:
        raise ValueError("unlisted_member_or_total_mismatch")
    return manifest, by_name


def verify(archive, expected_sha, destination=None):
    if digest(archive) != expected_sha:
        raise ValueError("archive_sha256_mismatch")
    if destination is not None and destination.exists():
        raise ValueError("restore_requires_new_destination_never_overlay")
    with archive.open("rb") as raw:
        bounded = BoundedMetadata(raw)
        with tarfile.open(fileobj=bounded, mode="r:") as tf:
            manifest, by_name = validate_archive(tf)
            bounded.metadata_phase = False
            parent = destination.parent if destination else None
            if parent:
                if not parent.is_dir():
                    raise ValueError("restore_parent_must_exist")
                if shutil.disk_usage(parent).free < manifest["total_bytes"] + 64 * 1024**2:
                    raise ValueError("insufficient_restore_disk")
            # Always validate every byte before creating the final destination.
            with context_stage(parent) as stage:
                for entry in manifest["files"]:
                    h = hashlib.sha256()
                    src = tf.extractfile(by_name["payload/" + entry["path"]])
                    target = local_path(stage, entry["path"]) if stage else None
                    if target:
                        target.parent.mkdir(parents=True, exist_ok=True)
                    with src, (target.open("wb") if target else open(os.devnull, "wb")) as out:
                        for data in iter(lambda: src.read(1024 * 1024), b""):
                            h.update(data); out.write(data)
                    if h.hexdigest() != entry["sha256"]:
                        raise ValueError(f"payload_sha256_mismatch:{entry['path']}")
                    if target:
                        target.chmod(0o755 if entry["executable"] else 0o644)
                receipt = {"status": "restored" if destination else "verified", "files": len(manifest["files"]), "archive_sha256": expected_sha, "claim_ceiling": manifest["claim_ceiling"]}
                if stage:
                    write_json(stage / "doc/host_transfer_manifest.json", manifest)
                    write_json(stage / "out/logs/host_transfer_restore_report.json", receipt)
                    publish_new(stage, destination)
                return receipt


class BoundedMetadata:
    """Reject huge PAX reads and total header work before allocating them."""
    def __init__(self, raw):
        self.raw = raw
        self.metadata_phase = True
        self.header_bytes = 0

    def __getattr__(self, name):
        return getattr(self.raw, name)

    def read(self, size=-1):
        if self.metadata_phase:
            if size < 0 or size > 1024**2 or self.header_bytes + size > 64 * 1024**2:
                raise ValueError("archive_metadata_budget_exceeded")
            self.header_bytes += size
        return self.raw.read(size)


from contextlib import contextmanager


@contextmanager
def context_stage(parent):
    if parent is None:
        yield None
    else:
        with tempfile.TemporaryDirectory(prefix=".forge_restore_", dir=parent) as tmp:
            yield Path(tmp)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="action", required=True)
    for action in ("plan", "create"):
        p = sub.add_parser(action)
        p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
        selection = p.add_mutually_exclusive_group(required=True)
        selection.add_argument("--include", action="append")
        selection.add_argument("--recipe", type=Path)
        p.add_argument("--output", required=True)
    for action in ("verify", "restore"):
        p = sub.add_parser(action)
        p.add_argument("--archive", type=Path, required=True)
        p.add_argument("--sha256", required=True)
        if action == "restore":
            p.add_argument("--destination", type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.action in ("plan", "create") and args.recipe:
            recipe = json.loads(args.recipe.read_text())
            if recipe.get("schema") != "forge_host_transfer_recipe.v1" or not isinstance(recipe.get("include"), list) or not recipe["include"]:
                raise ValueError("invalid_transfer_recipe")
            args.include = recipe["include"]
        if args.action == "plan":
            result = inventory(args.repo_root.resolve(), args.include)
            out = local_path(args.repo_root.resolve(), args.output)
            if out.relative_to(args.repo_root.resolve()).parts[0] != "out":
                raise ValueError("plan_report_must_live_under_out")
            write_json(out, result)
            result = {"status": "planned", "files": len(result["files"]), "bytes": result["total_bytes"], "report": str(out)}
        elif args.action == "create":
            result = create(args.repo_root.resolve(), args.include, args.output)
        else:
            dest = args.destination.absolute() if args.action == "restore" else None
            result = verify(args.archive, args.sha256, dest)
        print(json.dumps(result))
        return 0
    except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
