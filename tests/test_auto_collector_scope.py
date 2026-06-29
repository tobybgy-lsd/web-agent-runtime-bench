import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.auto_collect import collect_project


class AutoCollectorScopeTests(unittest.TestCase):
    def test_collect_project_is_scoped_and_skips_ignored_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "error.log").write_text("TimeoutError waiting for selector\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "secret.log").write_text("Bearer sk-node-module-secret", encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "config").write_text("token=sk-git-secret", encoding="utf-8")
            (root / ".venv").mkdir()
            (root / ".venv" / "pip.log").write_text("password=secret", encoding="utf-8")

            out = Path(tmp) / "out"
            manifest = collect_project(root, out, preset="auto")

            self.assertEqual(manifest["scope"]["allowed_root"], str(root.resolve()))
            copied = {item["relative_path"] for item in manifest["files"] if item["included"]}
            self.assertIn("error.log", copied)
            self.assertNotIn("node_modules/secret.log", copied)
            self.assertNotIn(".git/config", copied)
            self.assertNotIn(".venv/pip.log", copied)
            skipped = " ".join(item["relative_path"] for item in manifest["skipped_files"])
            self.assertIn("node_modules", skipped)
            self.assertIn(".git", skipped)

    def test_rejects_broad_scope_without_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = Path(tmp) / "out"
            with self.assertRaises(ValueError):
                collect_project(root, out, preset="auto")

    def test_dry_run_writes_manifest_but_copies_no_raw_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "error.log").write_text("net::ERR_PROXY_CONNECTION_FAILED\n", encoding="utf-8")
            out = Path(tmp) / "out"

            manifest = collect_project(root, out, preset="auto", dry_run=True)

            self.assertEqual(manifest["dry_run"], True)
            self.assertTrue((out / "collection_manifest.json").exists())
            self.assertFalse((out / "raw_local_only_do_not_share" / "error.log").exists())
            saved = json.loads((out / "collection_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["schema_version"], "collection_manifest/v1")

    def test_output_dir_can_live_inside_project_without_self_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "error.log").write_text("TimeoutError\n", encoding="utf-8")
            out = root / "failure_doctor_auto_report"

            manifest = collect_project(root, out, preset="auto", auto_diagnose=True)

            copied = {item["relative_path"] for item in manifest["files"] if item["included"]}
            self.assertIn("error.log", copied)
            self.assertFalse(any(path.startswith("failure_doctor_auto_report/") for path in copied))
            self.assertTrue((out / "open_this_first.md").exists())

