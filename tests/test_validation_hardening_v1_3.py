import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "validation" / "v1_3_validation_hardening.json"


class ValidationHardeningV13Tests(unittest.TestCase):
    def test_hardening_runner_writes_separate_track_summary(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_validation_hardening"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(SUMMARY_PATH.exists())

        payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "validation-hardening/v1.3")
        self.assertEqual(payload["version"], "v1.3")
        self.assertNotIn("single_accuracy_score", payload)
        self.assertEqual(payload["overall_gate"], "pass")

        tracks = {track["track_id"]: track for track in payload["tracks"]}
        expected_tracks = {
            "template_fixtures",
            "public_inspired_independent",
            "real_playwright_trace_semantic",
            "website_change_antibot",
            "external_public_reference",
            "external_heldout_public_source",
            "resolution_validation",
            "applied_scenario_validation",
            "integration_adapters",
        }
        self.assertTrue(expected_tracks.issubset(tracks))

        self.assertEqual(tracks["template_fixtures"]["evidence_tier"], "sanitized_template")
        self.assertEqual(tracks["real_playwright_trace_semantic"]["evidence_tier"], "native_trace")
        self.assertEqual(tracks["external_public_reference"]["evidence_tier"], "traceable_public_reference")
        self.assertEqual(tracks["integration_adapters"]["evidence_tier"], "workflow_smoke")

        for track in tracks.values():
            self.assertEqual(track["gate"], "pass", track["track_id"])
            self.assertEqual(track["forbidden_output_count"], 0, track["track_id"])
            self.assertIn("source_file", track)

    def test_hardening_summary_has_thresholds_and_regression_backlog(self):
        subprocess.run(
            [sys.executable, "-m", "tools.validation.run_validation_hardening"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=60,
            check=True,
        )
        payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

        thresholds = {item["track_id"]: item for item in payload["thresholds"]}
        self.assertEqual(thresholds["template_fixtures"]["min_reasonable_rate"], 0.85)
        self.assertEqual(thresholds["external_public_reference"]["min_actionable_rate"], 0.9)
        self.assertEqual(thresholds["resolution_validation"]["min_status_correct_rate"], 0.9)
        self.assertEqual(thresholds["integration_adapters"]["min_sample_count"], 4)

        backlog = payload["regression_backlog"]
        self.assertGreaterEqual(len(backlog), 4)
        self.assertTrue(
            any(item["reason"] == "severe_misclassification" for item in backlog),
            backlog,
        )
        self.assertTrue(
            any(item["reason"] == "insufficient_evidence" for item in backlog),
            backlog,
        )
        for item in backlog:
            self.assertFalse(item.get("safe_to_publish", True), item)

    def test_docs_expose_v1_3_hardening_pack(self):
        dashboard = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        report = (ROOT / "docs" / "VALIDATION_REPORT.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("v1.3 Validation Hardening Gate", dashboard)
        self.assertIn("validation/v1_3_validation_hardening.json", dashboard)
        self.assertIn("no single averaged accuracy score", dashboard)
        self.assertIn("v1.3 Validation Hardening Pack", report)
        self.assertIn("## v1.3.0", changelog)
        self.assertIn('version = "5.2.0"', pyproject)


if __name__ == "__main__":
    unittest.main()

