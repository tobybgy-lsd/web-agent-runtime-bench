from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VisualAgentRuntimeValidationTests(unittest.TestCase):
    def test_validation_runner_passes_thresholds(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_visual_agent_runtime_validation"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads((ROOT / "validation" / "visual_agent_runtime_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v3.6.0")
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 140)
        self.assertEqual(payload["external_vlm_call_count"], 0)
        self.assertEqual(payload["screenshot_upload_count"], 0)


if __name__ == "__main__":
    unittest.main()
