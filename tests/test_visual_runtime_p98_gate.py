from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VisualRuntimeP98GateTests(unittest.TestCase):
    def test_p98_gate_includes_visual_runtime_pillar(self) -> None:
        subprocess.run([sys.executable, "-m", "tools.validation.run_visual_agent_runtime_validation"], cwd=ROOT, check=True)
        proc = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_p98_master_gate"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v3.5.0")
        self.assertEqual(payload["overall_status"], "pass")
        self.assertIn("visual_agent_runtime_observability", payload["pillars"])


if __name__ == "__main__":
    unittest.main()
