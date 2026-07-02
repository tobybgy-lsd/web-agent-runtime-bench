from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class P95CoreTriageGateTests(unittest.TestCase):
    def test_runner_writes_machine_readable_p95_gate(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_p95_core_triage_gate"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads((ROOT / "validation" / "p95_core_triage_gate.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], "v2.4.1")
        self.assertEqual(payload["overall_status"], "pass")
        for pillar in (
            "playwright_trace_doctor",
            "cross_framework_adapters",
            "training_challenge_sedimentation",
            "composite_diagnosis",
            "safety_boundary",
        ):
            self.assertIn(pillar, payload["pillars"])
            self.assertEqual(payload["pillars"][pillar]["status"], "pass")


if __name__ == "__main__":
    unittest.main()

