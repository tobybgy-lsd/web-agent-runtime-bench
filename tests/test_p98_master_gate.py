import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class P98MasterGateTests(unittest.TestCase):
    def test_p98_master_gate_passes_only_with_all_pillars(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_p98_master_gate"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], "v3.4.0")
        self.assertEqual(payload["overall_status"], "pass")
        self.assertTrue(payload["final_p98_gate"])
        self.assertTrue(payload["ecosystem_score_excluded"])
        self.assertGreaterEqual(payload["controlled_maturity_score"], 98)
        self.assertEqual(payload["current_stable_line"], "v3.4.0")
        self.assertEqual(payload["previous_stable_line"], "v3.3.0")
        self.assertEqual(payload["global_forbidden_output_count"], 0)
        self.assertEqual(payload["global_private_solution_leak_count"], 0)
        self.assertEqual(payload["global_real_platform_access_count"], 0)
        self.assertEqual(payload["blocking_failures"], [])
        for pillar in payload["pillars"].values():
            self.assertEqual(pillar["status"], "pass")

    def test_p98_master_gate_has_no_target_only_missing_metrics(self):
        payload = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))

        for name, pillar in payload["pillars"].items():
            if name in {"safety_boundary", "release_docs_dashboard"}:
                continue
            self.assertIn("validation_file", pillar)
            self.assertTrue((ROOT / "validation" / pillar["validation_file"]).exists())
            self.assertIsNotNone(pillar["total_cases"], name)


if __name__ == "__main__":
    unittest.main()

