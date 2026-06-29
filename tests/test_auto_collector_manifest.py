import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.auto_collect import collect_project


class AutoCollectorManifestTests(unittest.TestCase):
    def test_manifest_schema_and_open_first_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "console.txt").write_text("locator.click: strict mode violation\n", encoding="utf-8")
            out = Path(tmp) / "auto_report"

            manifest = collect_project(root, out, preset="auto")

            self.assertEqual(manifest["schema_version"], "collection_manifest/v1")
            self.assertEqual(manifest["collector_version"], "3.2.0")
            self.assertEqual(manifest["safety"]["local_only"], True)
            self.assertEqual(manifest["safety"]["no_external_upload"], True)
            self.assertEqual(manifest["safety"]["no_browser_profile_access"], True)
            self.assertIsInstance(manifest["detected_frameworks"], list)
            self.assertTrue((out / "collection_summary.md").exists())
            self.assertTrue((out / "open_this_first.md").exists())
            self.assertTrue((out / "sanitized_failure_pack").exists())

            saved = json.loads((out / "collection_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["collector_version"], "3.2.0")

    def test_no_failure_signal_is_recorded_for_quiet_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "README.txt").write_text("normal successful run notes\n", encoding="utf-8")
            out = Path(tmp) / "auto_report"

            manifest = collect_project(root, out, preset="auto", auto_diagnose=True)

            self.assertIn("no_failure_signal_found", manifest["detected_failure_signals"])
            diagnosis = json.loads((out / "report" / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertIn(diagnosis["technical_category"], {"insufficient_evidence", "no_failure_signal_found"})

