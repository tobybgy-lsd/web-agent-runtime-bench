import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TraceDoctorCliTests(unittest.TestCase):
    def test_trace_doctor_diagnose_writes_standard_report_bundle(self):
        fixture_dir = ROOT / "examples" / "playwright_trace_cli"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trace_zip = root / "trace.zip"
            with zipfile.ZipFile(trace_zip, "w") as archive:
                archive.write(fixture_dir / "trace.trace", "trace.trace")
                archive.write(fixture_dir / "page.html", "resources/page.html")
            out_dir = root / "report"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "trace_doctor",
                    "diagnose",
                    str(trace_zip),
                    "--out",
                    str(out_dir),
                    "--run-id",
                    "trace_doctor_cli_test",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("selector_drift", result.stdout)

            expected_files = {
                "failure_artifact.json",
                "diagnosis.json",
                "diagnosis.md",
                "evidence.json",
                "issue_draft.md",
                "repair_suggestions.md",
                "trace_doctor_report.zip",
            }
            self.assertEqual(expected_files, {path.name for path in out_dir.iterdir() if path.is_file()})

            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
            evidence = json.loads((out_dir / "evidence.json").read_text(encoding="utf-8"))
            repair = (out_dir / "repair_suggestions.md").read_text(encoding="utf-8")

            self.assertEqual(diagnosis["failure_type"], "selector_drift")
            self.assertEqual(evidence["run_id"], "trace_doctor_cli_test")
            self.assertIn("failed_action", evidence["observations"])
            self.assertIn("Suggested Repair", repair)

            with zipfile.ZipFile(out_dir / "trace_doctor_report.zip") as archive:
                names = set(archive.namelist())
            self.assertIn("diagnosis.json", names)
            self.assertIn("evidence.json", names)
            self.assertIn("issue_draft.md", names)


if __name__ == "__main__":
    unittest.main()
