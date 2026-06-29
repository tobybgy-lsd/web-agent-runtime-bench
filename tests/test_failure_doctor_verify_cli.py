import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FailureDoctorVerifyCliTests(unittest.TestCase):
    def test_verify_command_compares_raw_input_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            before = tmp_path / "before"
            after = tmp_path / "after"
            out = tmp_path / "verification"
            before.mkdir()
            after.mkdir()
            (before / "error.log").write_text("Timeout waiting for selector .price; old selector resolved to 0 elements", encoding="utf-8")
            (after / "error.log").write_text("selector .amount matched; price field extracted", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "verify", "--before", str(before), "--after", str(after), "--out", str(out), "--create-regression"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((out / "verification_report.json").read_text(encoding="utf-8"))
            self.assertIn(report["status"], {"resolved", "changed_failure", "not_resolved", "insufficient_evidence"})
            self.assertTrue((out / "verification_report.md").exists())
            self.assertTrue((out / "regression_case.json").exists())
            regression = json.loads((out / "regression_case.json").read_text(encoding="utf-8"))
            self.assertFalse(regression["safe_to_publish"])


if __name__ == "__main__":
    unittest.main()
