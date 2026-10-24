#!/usr/bin/env python3
"""Resumable, workspace-local Linux provisioning; never qualifies a game build."""
from __future__ import annotations

import argparse
import contextlib
import ctypes
import hashlib
import json
import os
import errno
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as f:
        json.dump(value, f, indent=2); f.write("\n")
        tmp = Path(f.name)
    os.replace(tmp, path)


def local_path(root, relative):
    parts = PurePosixPath(relative)
    if not relative or parts.is_absolute() or any(p in ("", ".", "..") for p in relative.split("/")) or "\\" in relative or ":" in relative:
        raise ValueError(f"unsafe relative path: {relative}")
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes workspace: {relative}")
    return target


def publish_new(source, target):
    """Atomic no-clobber publication on Linux, including empty directories."""
    if source.is_dir():
        libc = ctypes.CDLL(None, use_errno=True)
        rename = getattr(libc, "renameat2", None)
        if rename is None:
            raise RuntimeError("atomic_directory_publication_unavailable")
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(-100, os.fsencode(source), -100, os.fsencode(target), 1):
            code = ctypes.get_errno()
            if code in (errno.EINVAL, errno.ENOSYS, errno.EOPNOTSUPP):
                raise RuntimeError("filesystem_lacks_atomic_directory_publish: use a native Linux workspace filesystem; keep the SD/FUSE archive as source")
            raise OSError(code, os.strerror(code), str(target))
    else:
        # link() is atomic and fails if ANY destination already exists.
        os.link(source, target)
        source.unlink()


@contextlib.contextmanager
def exclusive(root):
    import fcntl
    root.mkdir(parents=True, exist_ok=True)
    with (root / "bootstrap.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("bootstrap_busy: another installer owns this workspace") from exc
        yield


def download(spec, cache):
    """Cache key is content, not URL; bad/partial downloads never become ready."""
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / spec["sha256"]
    if target.exists():
        if digest(target) != spec["sha256"]:
            raise RuntimeError(f"cache_sha256_mismatch: {target}")
        return target
    if not spec["url"].startswith("https://"):
        raise ValueError("download requires HTTPS")
    tmp = target.with_suffix(".part")
    try:
        with urllib.request.urlopen(spec["url"], timeout=60) as response, tmp.open("wb") as out:
            if not response.url.startswith("https://"):
                raise RuntimeError("non_https_redirect")
            shutil.copyfileobj(response, out)
        if digest(tmp) != spec["sha256"]:
            raise RuntimeError(f"download_sha256_mismatch: {spec['url']}")
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)
    return target


def install_archive(repo, spec, run):
    target = local_path(repo, spec["target"])
    if target.exists():
        missing = [p for p in spec["required"] if not (target / p).is_file()]
        if missing:
            raise RuntimeError(f"existing_install_incomplete: {target}: {missing}; preserve and inspect manually")
        receipt = target / "forge_bootstrap_receipt.json"
        if receipt.exists():
            previous = json.loads(receipt.read_text())
            if previous["archive_sha256"] != spec["sha256"] or any(digest(target / p) != sha for p, sha in previous["files"].items()):
                raise RuntimeError(f"existing_install_changed: {target}; never overwrite a local SDK")
        return {"path": spec["target"], "status": "verified_receipt" if receipt.exists() else "existing_unmanaged_requires_route_check"}
    archive = download(spec, repo / "out/host_tools/downloads")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".forge_install_", dir=target.parent) as stage:
        stage = Path(stage)
        if spec["format"] == "7z":
            # Archive is an exact pinned upstream release, never arbitrary user input.
            run(["7z", "x", "-y", f"-o{stage}", str(archive)], "extract_sdk")
        else:
            with tarfile.open(archive) as tf:
                tf.extractall(stage, filter="data")
        payload = stage
        if spec["format"] == "tar_strip_root":
            dirs = list(stage.iterdir())
            if len(dirs) != 1 or not dirs[0].is_dir():
                raise RuntimeError("unexpected_archive_root")
            payload = dirs[0]
        for name in spec["required"]:
            path = payload / name
            if not path.is_file() or not path.resolve().is_relative_to(payload.resolve()):
                raise RuntimeError(f"archive_missing_required: {name}")
        if "pwsh" in spec["required"]:
            (payload / "pwsh").chmod(0o755)
        # All payload files are checked on subsequent runs, not just a marker.
        files = {p.relative_to(payload).as_posix(): digest(p) for p in sorted(payload.rglob("*")) if p.is_file()}
        write_json(payload / "forge_bootstrap_receipt.json", {"archive_sha256": spec["sha256"], "files": files})
        # Rename once after validation; a failed extraction cannot look installed.
        publish_new(payload, target)
    return {"path": spec["target"], "status": "installed_hash_verified"}


def environment(repo, catalog):
    venv = repo / "out/host_tools/python/venv"
    bins = [venv / "bin", repo / catalog["downloads"]["powershell"]["target"], repo / catalog["downloads"]["java"]["target"] / "bin", repo / "out/host_tools/rtk"]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "PIP_", "UV_"))}
    env.update({"PATH": os.pathsep.join(map(str, bins)) + os.pathsep + env.get("PATH", ""),
                "UV_CACHE_DIR": str(repo / "out/host_tools/uv_cache"),
                "UV_TOOL_DIR": str(repo / "out/host_tools/uv_tools"),
                "UV_TOOL_BIN_DIR": str(venv / "bin"), "UV_PYTHON_DOWNLOADS": "never",
                "PIP_CACHE_DIR": str(repo / "out/host_tools/pip_cache"),
                "PYTHONNOUSERSITE": "1", "GDK": str(repo / "sdk/sgdk-2.11"),
                "MD_ROOT": str(repo), "MAKEFLAGS": "-j1"})
    return env


def activate(repo, catalog):
    env = environment(repo, catalog)
    # Resolve relative to this generated file so workspace moves do not retain
    # old absolute paths. Venvs are recreated, never transferred between hosts.
    script = '# Source this file in bash; do not execute it.\n'
    script += 'forge_repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"\n'
    for key in ("UV_CACHE_DIR", "UV_TOOL_DIR", "UV_TOOL_BIN_DIR", "PIP_CACHE_DIR", "GDK", "MD_ROOT"):
        relative = Path(env[key]).relative_to(repo).as_posix()
        script += f'export {key}="$forge_repo/{relative}"\n'
    pwsh = catalog["downloads"]["powershell"]["target"]
    java = catalog["downloads"]["java"]["target"]
    script += f'export PATH="$forge_repo/out/host_tools/python/venv/bin:$forge_repo/{pwsh}:$forge_repo/{java}/bin:$forge_repo/out/host_tools/rtk:$PATH"\n'
    script += 'export MAKEFLAGS=-j1 PYTHONNOUSERSITE=1 UV_PYTHON_DOWNLOADS=never\nunset forge_repo\n'
    target = repo / "out/host_tools/activate.sh"
    target.write_text(script, encoding="utf-8")


def provision(repo, catalog, profile, run):
    result = {}
    # Fail before large downloads on filesystems that cannot honor no-clobber
    # directory publication (observed on this workspace's SD/FUSE mount).
    with tempfile.TemporaryDirectory(prefix=".publication_probe_", dir=repo / "out/host_tools") as tmp:
        probe = Path(tmp) / "source"; probe.mkdir()
        publish_new(probe, Path(tmp) / "destination")
    result["directory_publication"] = "atomic_no_clobber_supported"
    for name, spec in catalog["downloads"].items():
        result[name] = install_archive(repo, spec, run)
    venv = repo / "out/host_tools/python/venv"
    if not (venv / "bin/python").exists():
        if venv.exists():
            raise RuntimeError("partial_venv_present: inspect before removing")
        run([sys.executable, "-m", "venv", str(venv)], "create_venv")
    lock = repo / "tools/sgdk_wrapper/host_python_requirements.lock"
    marker = venv / "forge_lock.sha256"
    # Recheck installed packages even if the lock stamp matches.
    run([str(venv / "bin/python"), "-m", "pip", "install", "--require-hashes", "--only-binary=:all:", "-r", str(lock)], "python_dependencies")
    run([str(venv / "bin/python"), "-m", "pip", "check"], "python_check")
    marker.write_text(digest(lock) + "\n")
    activate(repo, catalog)
    run(["pwsh", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"], "pwsh_probe")
    run(["java", "-version"], "java_probe")
    run(["rtk", "--version"], "rtk_probe")
    if profile == "full":
        for entry in catalog["flatpaks"]:
            # Existing different versions are a blocker, never a silent downgrade.
            probe = subprocess.run(["flatpak", "--user", "info", "--show-commit", entry["ref"]], capture_output=True, text=True, timeout=30)
            if probe.returncode == 0 and probe.stdout.strip() != entry["commit"]:
                raise RuntimeError(f"flatpak_commit_mismatch: {entry['ref']}; preserve current installation and review explicitly")
            if probe.returncode:
                run(["flatpak", "--user", "remote-add", "--if-not-exists", "flathub", "https://flathub.org/repo/flathub.flatpakrepo"], "flatpak_remote")
                run(["flatpak", "--user", "install", "-y", "--noninteractive", "flathub", entry["ref"]], "flatpak_install")
                run(["flatpak", "--user", "update", "-y", "--noninteractive", "--commit=" + entry["commit"], entry["ref"]], "flatpak_pin")
            verify = subprocess.run(["flatpak", "--user", "info", "--show-commit", entry["ref"]], capture_output=True, text=True, timeout=30)
            if verify.returncode or verify.stdout.strip() != entry["commit"]:
                raise RuntimeError("flatpak_commit_verification_failed")
            runtime = subprocess.run(["flatpak", "--user", "info", "--show-runtime", entry["ref"]], capture_output=True, text=True, timeout=30)
            runtime_ref = runtime.stdout.strip()
            if runtime.returncode or not re.fullmatch(r"[\w.-]+/x86_64/[\w.-]+", runtime_ref):
                raise RuntimeError("flatpak_runtime_identity_unreadable")
            runtime_ref = "runtime/" + runtime_ref
            available = subprocess.run(["flatpak", "--user", "info", runtime_ref], capture_output=True, text=True, timeout=30)
            if available.returncode:
                run(["flatpak", "--user", "remote-add", "--if-not-exists", "flathub", "https://flathub.org/repo/flathub.flatpakrepo"], "flatpak_runtime_remote")
                run(["flatpak", "--user", "install", "-y", "--noninteractive", "flathub", runtime_ref], "flatpak_runtime_install")
                available = subprocess.run(["flatpak", "--user", "info", runtime_ref], capture_output=True, text=True, timeout=30)
                if available.returncode:
                    raise RuntimeError(f"flatpak_runtime_still_missing:{runtime_ref}")
            result.setdefault("flatpaks", []).append({"ref": entry["ref"], "commit": entry["commit"], "runtime": runtime_ref})
        run(["flatpak", "--user", "run", "--command=wine", "org.winehq.Wine//wow64-24.08", "--version"], "wine_runtime_probe")
        legacy = repo / "tools/sgdk_wrapper/linux_host_dependencies.json"
        if legacy.is_file():
            old = json.loads(legacy.read_text())["blastem_linux"]["commit"]
            current = next(e["commit"] for e in catalog["flatpaks"] if "com.retrodev.blastem" in e["ref"])
            if old != current:
                result["capture_identity_gate"] = {"status": "blocked_legacy_catalog_identity_drift", "legacy_commit": old, "provisioned_commit": current, "next": "Bind actual emulator identity at session launch and seal; requalify route before new capture claims. Never relabel historical bundles."}
        bridge = repo / "tools/sgdk_wrapper/session_bridge/build.sh"
        if not bridge.is_file():
            raise RuntimeError("session_bridge_source_missing: restore private transfer; clone alone is not continuity")
        run(["bash", str(bridge)], "build_virtual_pads", cwd=bridge.parent)
        maintenance = repo / "tools/sgdk_wrapper/blastem_maintenance.py"
        if not maintenance.is_file():
            raise RuntimeError("blastem_maintenance_source_missing: restore private transfer")
        run([str(venv / "bin/python"), str(maintenance), "install", "--repo-root", str(repo), "--output", str(repo / "out/logs/blastem_bootstrap_maintenance.json")], "diagnostic_blastem_install")
        run(["pwsh", "-NoProfile", "-File", str(repo / "tools/sgdk_wrapper/assert_agent_environment.ps1"), "-NoInstallMissing"], "agent_environment")
    return result


def diagnose(repo, catalog, profile):
    blockers = []
    if platform.system() != "Linux" or platform.machine().lower() not in ("x86_64", "amd64"):
        blockers.append("unsupported_host_requires_linux_x86_64")
    if sys.version_info < (3, 11):
        blockers.append("python_3_11_required")
    free = shutil.disk_usage(repo).free
    minimum = catalog["minimum_free_gib"] if profile == "full" else catalog["minimum_portable_free_gib"]
    if free < minimum * 1024**3:
        blockers.append("insufficient_disk_for_install_and_sdk_staging")
    required = ["7z"] + (["flatpak", "gcc", "make", "flock", "Xvfb", "xauth", "xwininfo", "xdotool", "import", "ffmpeg", "dbus-run-session"] if profile == "full" else [])
    commands = {name: shutil.which(name) for name in required}
    blockers.extend(f"missing_system_command:{name}" for name, value in commands.items() if not value)
    return {"system": platform.system(), "machine": platform.machine(), "python": platform.python_version(), "free_bytes": free, "commands": commands, "blockers": blockers}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=REPO)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--profile", choices=("portable", "full"), default="full")
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    catalog = json.loads((HERE / "bootstrap_host.json").read_text())
    report = {"schema": "forge_host_bootstrap_report.v1", "profile": args.profile, "claim_ceiling": catalog["claim_ceiling"], "game_qa": "not_executed", "steps": [], "diagnosis": diagnose(repo, catalog, args.profile)}
    root = local_path(repo, "out/host_tools")
    output = local_path(repo, "out/logs/host_bootstrap_report.json")
    env = environment(repo, catalog)

    def run(argv, name, cwd=None):
        log = root / "bootstrap_logs" / f"{len(report['steps']):02d}_{name}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        print(f"bootstrap_step={name} log={log.relative_to(repo)}", flush=True)
        step = {"name": name, "argv": argv, "log": log.relative_to(repo).as_posix()}
        report["steps"].append(step)
        with log.open("w") as stream:
            try:
                proc = subprocess.run(argv, cwd=cwd or repo, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=900)
                step["exit_code"] = proc.returncode
            except subprocess.TimeoutExpired as exc:
                step["status"] = "timeout"
                raise RuntimeError(f"step_timeout: {name}; inspect owned subprocesses before retry") from exc
        step["log_sha256"] = digest(log)
        if proc.returncode:
            raise RuntimeError(f"step_failed:{name}:{proc.returncode}; see {log}")

    try:
        if not args.apply:
            report["status"] = "plan_only"
        elif report["diagnosis"]["blockers"]:
            raise RuntimeError("; ".join(report["diagnosis"]["blockers"]))
        elif os.geteuid() == 0:
            raise RuntimeError("run_as_developer_not_root")
        else:
            with exclusive(root):
                report["installed"] = provision(repo, catalog, args.profile, run)
            report["status"] = "dependencies_provisioned" if args.profile == "full" else "portable_only_system_and_emulator_pending"
        report["resource_policy"] = {"workers": 1, "emulator_sessions": 1, "automatic_cleanup": False, "parallel_builds": False}
    except (OSError, ValueError, RuntimeError, tarfile.TarError, subprocess.SubprocessError) as exc:
        report.update(status="blocked", error=str(exc))
    # Even failures leave an actionable report. No existing project evidence is touched.
    write_json(output, report)
    print(json.dumps({"status": report["status"], "report": str(output), "claim_ceiling": report["claim_ceiling"]}))
    return 1 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
