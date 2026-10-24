"""Host-only tests: these intentionally make no ROM, FPS or listening claim."""
import hashlib
import io
import json
import os
import subprocess
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bootstrap_host as host
import host_transfer as transfer


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "workspace with spaces"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "src/game.c").write_text("uncommitted source\n")
        (self.repo / "src/.env").write_text("secret")
        (self.repo / "src/out").mkdir()
        (self.repo / "src/out/keep.bin").write_bytes(b"evidence")

    def roundtrip(self):
        receipt = transfer.create(self.repo, ["src", "src/out/keep.bin"], "out/transfer/private.tar")
        archive = self.repo / receipt["archive"]
        return receipt, archive

    def test_paths_reject_escape_aliases_and_windows_paths(self):
        for rel in ("", ".", "..", "a/../b", "/tmp/a", "C:/a", "a\\b", "a//b", "a/./b", "a/"):
            with self.subTest(rel=rel), self.assertRaises(ValueError):
                host.local_path(self.repo, rel)

    def test_external_symlink_rejected_before_writing(self):
        (self.repo / "src/link").symlink_to("/etc/hosts")
        with self.assertRaisesRegex(ValueError, "escapes|external"):
            transfer.inventory(self.repo, ["src"])

    def test_internal_file_alias_materialized(self):
        (self.repo / "src/alias.c").symlink_to("game.c")
        receipt, archive = self.roundtrip()
        dest = Path(self.tmp.name) / "restore"
        transfer.verify(archive, receipt["sha256"], dest)
        self.assertFalse((dest / "src/alias.c").is_symlink())
        self.assertEqual((dest / "src/alias.c").read_bytes(), (dest / "src/game.c").read_bytes())

    def test_internal_directory_alias_materialized_without_cycles(self):
        (self.repo / "source_data").mkdir(); (self.repo / "source_data/asset.txt").write_text("authored")
        (self.repo / "src/alias").symlink_to("../source_data", target_is_directory=True)
        receipt, archive = self.roundtrip()
        dest = Path(self.tmp.name) / "restore"
        transfer.verify(archive, receipt["sha256"], dest)
        self.assertFalse((dest / "src/alias").is_symlink())
        self.assertEqual((dest / "src/alias/asset.txt").read_text(), "authored")

    def test_directory_alias_cycle_rejected(self):
        (self.repo / "src/loop").symlink_to(".", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "alias_cycle"):
            transfer.inventory(self.repo, ["src"])

    def test_arbitrarily_named_virtual_environment_is_not_transferred(self):
        venv = self.repo / "src/final_wheel_env"; (venv / "bin").mkdir(parents=True)
        (venv / "pyvenv.cfg").write_text("home = /old/host")
        (venv / "bin/python").symlink_to("/usr/bin/python3")
        inv = transfer.inventory(self.repo, ["src"])
        self.assertEqual([e["path"] for e in inv["files"]], ["src/game.c"])
        self.assertTrue(any("virtualenv_recreate" in x for x in inv["skipped"]))

    def test_canonical_skill_tree_preserved_local_bridge_skipped(self):
        canonical = self.repo / "tools/sgdk_wrapper/.agent/skills"
        canonical.mkdir(parents=True)
        (canonical / "lesson.md").write_text("expertise")
        (self.repo / "src/.agent").symlink_to(canonical.parent, target_is_directory=True)
        inv = transfer.inventory(self.repo, ["tools", "src"])
        self.assertIn("tools/sgdk_wrapper/.agent/skills/lesson.md", [e["path"] for e in inv["files"]])
        self.assertNotIn("src/.agent", [e["path"] for e in inv["files"]])

    def test_ignored_sources_and_explicit_evidence_transferred(self):
        receipt, archive = self.roundtrip()
        dest = Path(self.tmp.name) / "restore"
        result = transfer.verify(archive, receipt["sha256"], dest)
        self.assertEqual(result["status"], "restored")
        self.assertEqual((dest / "src/out/keep.bin").read_bytes(), b"evidence")
        self.assertEqual((dest / "src/game.c").read_text(), "uncommitted source\n")
        self.assertFalse((dest / "src/.env").exists())
        self.assertFalse((dest / ".git").exists())

    def test_payload_crossing_copy_blocks_restores_exact_bytes(self):
        payload = b"bounded io block" * 140001
        (self.repo / "src/large.dat").write_bytes(payload)
        receipt, archive = self.roundtrip()
        dest = Path(self.tmp.name) / "restore"
        transfer.verify(archive, receipt["sha256"], dest)
        self.assertEqual((dest / "src/large.dat").read_bytes(), payload)

    def test_forbidden_explicit_scope_rejected(self):
        for name in (".git", ".ssh", "src/.env", "src/.env.local", "src/.env.local/inner", "src/signing.key", "src/client.pem", "out/host_tools"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "forbidden_scope"):
                transfer.inventory(self.repo, [name])

    def test_internal_alias_cannot_bypass_secret_filter(self):
        (self.repo / "src/alias.c").symlink_to(".env")
        with self.assertRaisesRegex(ValueError, "sensitive_symlink"):
            transfer.inventory(self.repo, ["src"])

    def test_scope_through_secret_directory_alias_rejected(self):
        secrets = self.repo / ".ssh"; secrets.mkdir(); (secrets / "id_ed25519").write_text("SECRET")
        (self.repo / "src/alias").symlink_to("../.ssh", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "sensitive_symlink"):
            transfer.inventory(self.repo, ["src/alias/id_ed25519"])

    def test_large_legitimate_manifest_survives_header_guard(self):
        empty_sha = hashlib.sha256(b"").hexdigest()
        files = [{"path": f"src/file_{i:05d}_with_descriptive_name.txt", "size": 0, "sha256": empty_sha, "executable": False} for i in range(8000)]
        manifest = {"schema": "forge_host_transfer.v1", "private": True, "files": files, "total_bytes": 0, "claim_ceiling": "byte_identity_only_no_new_game_qa"}
        self.assertGreater(len(json.dumps(manifest).encode()), 1024**2)
        entries = []
        for file in files:
            info = tarfile.TarInfo("payload/" + file["path"]); info.size = 0
            entries.append((info, b""))
        archive = self.malicious(entries, manifest)
        result = transfer.verify(archive, host.digest(archive))
        self.assertEqual(result["files"], 8000)

    def test_real_local_agent_customizations_preserved(self):
        local = self.repo / "src/.agent"
        local.mkdir(); (local / "custom.md").write_text("local specialization")
        inv = transfer.inventory(self.repo, ["src"])
        self.assertIn("src/.agent/custom.md", [e["path"] for e in inv["files"]])

    def test_atomic_file_publication_never_clobbers(self):
        source = self.repo / "candidate"; source.write_text("candidate")
        dest = self.repo / "published"; dest.write_text("another exporter")
        with self.assertRaises(FileExistsError):
            host.publish_new(source, dest)
        self.assertEqual(dest.read_text(), "another exporter")
        self.assertTrue(source.exists())

    def test_atomic_directory_publication_never_clobbers_empty_directory(self):
        source = self.repo / "candidate"; source.mkdir(); (source / "file").write_text("candidate")
        dest = self.repo / "published"; dest.mkdir()
        with self.assertRaises(FileExistsError):
            host.publish_new(source, dest)
        self.assertEqual(list(dest.iterdir()), [])
        self.assertTrue((source / "file").exists())

    def test_header_reader_refuses_unbounded_pax_allocation(self):
        reader = transfer.BoundedMetadata(io.BytesIO(b""))
        with self.assertRaisesRegex(ValueError, "metadata_budget"):
            reader.read(1024**2 + 1)
        reader.header_bytes = 64 * 1024**2
        with self.assertRaisesRegex(ValueError, "metadata_budget"):
            reader.read(512)

    def test_existing_unmanaged_sdk_is_preserved_and_explicit(self):
        sdk = self.repo / "sdk"; sdk.mkdir(); (sdk / "makefile.gen").write_text("custom")
        result = host.install_archive(self.repo, {"target": "sdk", "required": ["makefile.gen"]}, mock.Mock())
        self.assertEqual(result["status"], "existing_unmanaged_requires_route_check")

    def test_archive_and_restore_destinations_never_overwritten(self):
        receipt, archive = self.roundtrip()
        with self.assertRaisesRegex(ValueError, "never_overwrite"):
            transfer.create(self.repo, ["src"], receipt["archive"])
        with self.assertRaisesRegex(ValueError, "never_overlay"):
            transfer.verify(archive, receipt["sha256"], self.repo)

    def test_bad_archive_hash_creates_no_destination(self):
        _, archive = self.roundtrip()
        dest = Path(self.tmp.name) / "restore"
        with self.assertRaisesRegex(ValueError, "archive_sha256"):
            transfer.verify(archive, "0" * 64, dest)
        self.assertFalse(dest.exists())

    def malicious(self, entries, manifest=None):
        archive = Path(self.tmp.name) / "malicious.tar"
        with tarfile.open(archive, "w") as tf:
            if manifest is not None:
                raw = json.dumps(manifest).encode()
                info = tarfile.TarInfo("manifest.json"); info.size = len(raw)
                tf.addfile(info, io.BytesIO(raw))
            for info, raw in entries:
                tf.addfile(info, io.BytesIO(raw) if raw is not None else None)
        return archive

    def test_tar_symlink_pivot_rejected(self):
        info = tarfile.TarInfo("payload/link"); info.type = tarfile.SYMTYPE; info.linkname = "/tmp"
        archive = self.malicious([(info, None)])
        with self.assertRaisesRegex(ValueError, "regular_files"):
            transfer.verify(archive, host.digest(archive))

    def test_tar_duplicate_member_rejected(self):
        info = tarfile.TarInfo("manifest.json"); info.size = 2
        archive = self.malicious([(info, b"{}"), (info, b"{}")])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            transfer.verify(archive, host.digest(archive))

    def test_tar_traversal_rejected_even_with_valid_outer_hash(self):
        info = tarfile.TarInfo("payload/../escape"); info.size = 1
        manifest = {"schema": "forge_host_transfer.v1", "private": True, "files": [{"path": "../escape", "size": 1, "sha256": hashlib.sha256(b"x").hexdigest()}], "total_bytes": 1}
        archive = self.malicious([(info, b"x")], manifest)
        with self.assertRaisesRegex(ValueError, "unsafe relative"):
            transfer.verify(archive, host.digest(archive))

    def test_payload_hash_rejected_without_partial_restore(self):
        info = tarfile.TarInfo("payload/src/a"); info.size = 1
        manifest = {"schema": "forge_host_transfer.v1", "private": True, "files": [{"path": "src/a", "size": 1, "sha256": "0" * 64}], "total_bytes": 1}
        archive = self.malicious([(info, b"x")], manifest)
        dest = Path(self.tmp.name) / "restore"
        with self.assertRaisesRegex(ValueError, "payload_sha256"):
            transfer.verify(archive, host.digest(archive), dest)
        self.assertFalse(dest.exists())
        self.assertFalse(list(dest.parent.glob(".forge_restore_*")))

    def test_mutation_during_export_does_not_publish(self):
        original = transfer.inventory
        def mutated(*args):
            result = original(*args)
            (self.repo / "src/game.c").write_text("changed contents!!\n")
            return result
        with mock.patch.object(transfer, "inventory", mutated), self.assertRaises((ValueError, OSError)):
            transfer.create(self.repo, ["src"], "out/transfer/private.tar")
        self.assertFalse((self.repo / "out/transfer/private.tar").exists())
        self.assertFalse(list((self.repo / "out/transfer").glob("*.partial")))

    def test_missing_scope_blocks_transfer(self):
        with self.assertRaisesRegex(ValueError, "required_scope_missing"):
            transfer.inventory(self.repo, ["missing"])

    def test_no_root_pollution_from_archive_or_plan(self):
        with self.assertRaisesRegex(ValueError, "under_workspace_out"):
            transfer.create(self.repo, ["src"], "root.tar")

    def test_cached_download_requires_content_hash(self):
        cache = self.repo / "cache"; cache.mkdir()
        (cache / ("0" * 64)).write_bytes(b"bad")
        with self.assertRaisesRegex(RuntimeError, "cache_sha256"):
            host.download({"sha256": "0" * 64, "url": "https://invalid.example"}, cache)

    def test_download_rejects_plain_http(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            host.download({"sha256": "0" * 64, "url": "http://invalid.example"}, self.repo / "cache")

    def test_failed_download_does_not_leave_installable_cache(self):
        data = io.BytesIO(b"bad payload"); data.url = "https://example.test/file"
        cache = self.repo / "cache"
        with mock.patch.object(host.urllib.request, "urlopen", return_value=data), self.assertRaisesRegex(RuntimeError, "download_sha256"):
            host.download({"sha256": "0" * 64, "url": data.url}, cache)
        self.assertEqual(list(cache.iterdir()), [])

    def test_partial_existing_sdk_never_overwritten(self):
        sdk = self.repo / "sdk/sgdk-2.11"; sdk.mkdir(parents=True)
        (sdk / "important.c").write_text("local change")
        with self.assertRaisesRegex(RuntimeError, "existing_install_incomplete"):
            host.install_archive(self.repo, {"target": "sdk/sgdk-2.11", "required": ["bin/gcc.exe"]}, mock.Mock())
        self.assertEqual((sdk / "important.c").read_text(), "local change")

    def test_changed_installed_file_blocks_idempotent_run(self):
        target = self.repo / "tool"; target.mkdir()
        (target / "binary").write_bytes(b"changed")
        host.write_json(target / "forge_bootstrap_receipt.json", {"archive_sha256": "0" * 64, "files": {"binary": hashlib.sha256(b"original").hexdigest()}})
        with self.assertRaisesRegex(RuntimeError, "existing_install_changed"):
            host.install_archive(self.repo, {"target": "tool", "required": ["binary"], "sha256": "0" * 64}, mock.Mock())

    def test_concurrent_install_refused(self):
        with host.exclusive(self.repo / "out/host_tools"):
            with self.assertRaisesRegex(RuntimeError, "bootstrap_busy"):
                with host.exclusive(self.repo / "out/host_tools"):
                    self.fail("second installer entered")

    def test_activation_does_not_embed_old_absolute_host_path(self):
        catalog = json.loads((host.HERE / "bootstrap_host.json").read_text())
        (self.repo / "out/host_tools").mkdir(parents=True)
        host.activate(self.repo, catalog)
        text = (self.repo / "out/host_tools/activate.sh").read_text()
        self.assertNotIn(str(self.repo), text)
        self.assertIn("BASH_SOURCE", text)
        self.assertIn("MAKEFLAGS=-j1", text)

    def test_unsupported_host_diagnosed_without_install(self):
        catalog = json.loads((host.HERE / "bootstrap_host.json").read_text())
        with mock.patch.object(host.platform, "system", return_value="Darwin"):
            result = host.diagnose(self.repo, catalog, "portable")
        self.assertIn("unsupported_host_requires_linux_x86_64", result["blockers"])

    def prepared_provision(self):
        catalog = json.loads((host.HERE / "bootstrap_host.json").read_text())
        venv = self.repo / "out/host_tools/python/venv"; (venv / "bin").mkdir(parents=True)
        (venv / "bin/python").write_text("fake executable")
        wrapper = self.repo / "tools/sgdk_wrapper"; (wrapper / "session_bridge").mkdir(parents=True)
        (wrapper / "session_bridge/build.sh").write_text("fake source")
        (wrapper / "blastem_maintenance.py").write_text("fake source")
        (wrapper / "host_python_requirements.lock").write_text("test lock")
        host.write_json(wrapper / "linux_host_dependencies.json", {"blastem_linux": {"commit": "old"}})
        return catalog

    def test_missing_flatpak_runtime_repaired_even_if_app_is_installed(self):
        catalog = self.prepared_provision()
        runtime_queries = {}
        def query(argv, **kwargs):
            code, out = 0, ""
            if "--show-commit" in argv:
                out = next(e["commit"] for e in catalog["flatpaks"] if e["ref"] == argv[-1])
            elif "--show-runtime" in argv:
                out = "org.freedesktop.Platform/x86_64/24.08"
            elif argv[-1].startswith("runtime/"):
                runtime_queries[argv[-1]] = runtime_queries.get(argv[-1], 0) + 1
                code = int(runtime_queries[argv[-1]] == 1)
            return subprocess.CompletedProcess(argv, code, stdout=out, stderr="")
        run = mock.Mock()
        with mock.patch.object(host, "install_archive", return_value={}), mock.patch.object(host.subprocess, "run", side_effect=query):
            result = host.provision(self.repo, catalog, "full", run)
        self.assertTrue(any(c.args[1] == "flatpak_runtime_install" for c in run.call_args_list))
        self.assertEqual(result["capture_identity_gate"]["status"], "blocked_legacy_catalog_identity_drift")
        self.assertTrue(any(c.args[1] == "wine_runtime_probe" for c in run.call_args_list))

    def test_existing_other_flatpak_commit_is_not_downgraded(self):
        catalog = self.prepared_provision()
        run = mock.Mock()
        other = subprocess.CompletedProcess([], 0, stdout="different", stderr="")
        with mock.patch.object(host, "install_archive", return_value={}), mock.patch.object(host.subprocess, "run", return_value=other), self.assertRaisesRegex(RuntimeError, "flatpak_commit_mismatch"):
            host.provision(self.repo, catalog, "full", run)
        self.assertFalse(any("flatpak" in c.args[0][0] for c in run.call_args_list))


if __name__ == "__main__":
    unittest.main()
