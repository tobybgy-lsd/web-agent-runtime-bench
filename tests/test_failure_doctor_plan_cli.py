import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FailureDoctorPlanCliTests(unittest.TestCase):
    def test_plan_command_reads_report_and_writes_fix_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_dir = tmp_path / "failed"
            report_dir = tmp_path / "report"
            plan_dir = tmp_path / "fix_plan"
            input_dir.mkdir()
            (input_dir / "error.log").write_text("locator.click: Error: strict mode violation: locator('button') resolved to 2 elements", encoding="utf-8")
            diagnose = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(report_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(diagnose.returncode, 0, diagnose.stdout + diagnose.stderr)
            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "plan", str(report_dir), "--out", str(plan_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((plan_dir / "fix_plan.json").exists())
            self.assertTrue((plan_dir / "fix_plan.md").exists())
            self.assertTrue((plan_dir / "codex_fix_prompt.md").exists())
            plan = json.loads((plan_dir / "fix_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["schema_version"], "fix_plan/v1")
            self.assertEqual(plan["failure_type"], "playwright_strict_mode_violation")


if __name__ == "__main__":
    unittest.main()
