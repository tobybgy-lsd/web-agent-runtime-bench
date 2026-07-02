from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _process_output(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or "") + (result.stdout or "")


class FailureDoctorAdaptCliTests(unittest.TestCase):
    def test_adapt_pack_can_be_diagnosed_and_planned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            (source / "error.log").write_text(
                "TimeoutError: waiting for selector .checkout failed: timeout 30000ms exceeded",
                encoding="utf-8",
            )
            pack = root / "pack"
            report = root / "report"
            plan = root / "plan"

            adapt = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "failure_doctor",
                    "adapt",
                    str(source),
                    "--framework",
                    "puppeteer",
                    "--out",
                    str(pack),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(adapt.returncode, 0, _process_output(adapt))

            diagnose = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(pack), "--out", str(report)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(diagnose.returncode, 0, _process_output(diagnose))
            diagnosis = json.loads((report / "diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(diagnosis["technical_category"], "selector_drift")
            self.assertEqual(diagnosis["subtype"], "puppeteer_selector_timeout")

            plan_run = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "plan", str(report), "--out", str(plan)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(plan_run.returncode, 0, _process_output(plan_run))
            self.assertTrue((plan / "codex_fix_prompt.md").exists())


if __name__ == "__main__":
    unittest.main()

