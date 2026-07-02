from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.validation.run_visual_agent_runtime_validation import ensure_cases


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "visual_agent_runtime_cases" / "coordinate_click_drift_001" / "visual_run"


class VisualRuntimeCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ensure_cases()

    def test_visual_runtime_help_exposes_commands(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "visual-runtime", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("diagnose", proc.stdout)
        self.assertIn("compare", proc.stdout)
        self.assertIn("adapt", proc.stdout)

    def test_visual_runtime_diagnose_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "visual_report"
            proc = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "visual-runtime", "diagnose", "--input", str(CASE), "--out", str(out), "--dom-optional"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            diagnosis = json.loads((out / "visual_runtime_diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(diagnosis["subtype"], "coordinate_click_drift")
            self.assertTrue((out / "open_this_first_visual.md").exists())

    def test_visual_runtime_profile_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "profile"
            proc = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "visual-runtime", "profile", "--input", str(CASE), "--out", str(out), "--dom-optional"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            profile = json.loads((out / "visual_runtime_profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["schema_version"], "visual_runtime_profile/v1")

            valid_out = Path(tmp) / "validation"
            proc = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "visual-runtime", "validate", "--input", str(CASE), "--out", str(valid_out), "--dom-optional"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()

