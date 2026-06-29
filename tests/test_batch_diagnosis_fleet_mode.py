import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BatchDiagnosisFleetModeTests(unittest.TestCase):
    def test_batch_diagnoses_multiple_runs_and_writes_fleet_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runs_dir = tmp_path / "runs"
            runs_dir.mkdir()
            self._write_run(runs_dir / "run_001_proxy", "page.goto: net::ERR_PROXY_CONNECTION_FAILED")
            self._write_run(runs_dir / "run_002_proxy_repeat", "page.goto: net::ERR_PROXY_CONNECTION_FAILED")
            self._write_run(runs_dir / "run_003_selector", "locator.click: Timeout waiting for selector .price")
            self._write_run(runs_dir / "run_004_rate_limit", "HTTP 429 Too Many Requests")

            out_dir = tmp_path / "batch_report"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "batch",
                    str(runs_dir),
                    "--out",
                    str(out_dir),
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            expected = {
                "summary.json",
                "summary.md",
                "failures_by_type.csv",
                "top_root_causes.md",
                "repeated_failures.md",
                "suggested_regression_cases.md",
                "repair_priority.md",
            }
            self.assertTrue(expected.issubset({path.name for path in out_dir.iterdir()}))
            self.assertTrue((out_dir / "reports" / "run_001_proxy" / "diagnosis.json").exists())

            summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["schema_version"], "batch_diagnosis/v1")
            self.assertEqual(summary["total_runs"], 4)
            self.assertEqual(summary["diagnosed_runs"], 4)
            self.assertGreaterEqual(summary["repeated_failures_count"], 1)
            self.assertTrue(summary["repair_priority"])
            self.assertTrue(summary["suggested_regression_cases"])
            self.assertEqual(summary["forbidden_output_count"], 0)

            with (out_dir / "failures_by_type.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(rows)
            self.assertIn("technical_category", rows[0])
            self.assertIn("count", rows[0])

            repeated = (out_dir / "repeated_failures.md").read_text(encoding="utf-8")
            self.assertIn("network_http_error", repeated)
            priority = (out_dir / "repair_priority.md").read_text(encoding="utf-8")
            self.assertIn("run_001_proxy", priority)

    def test_docs_and_version_expose_batch_mode_under_current_release(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "2.4.1"', pyproject)
        self.assertIn("v2.4.1 P95 Alignment & Missing Tracks Pack", readme)
        self.assertIn("v3.0.x P98 Controlled Maturity Pack", readme)
        self.assertIn("Batch Diagnosis / Fleet Mode", readme)
        self.assertIn("failure-doctor batch", readme)
        self.assertIn("## v3.0.0", changelog)

    def _write_run(self, path: Path, error_text: str) -> None:
        path.mkdir()
        (path / "error.log").write_text(error_text + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
