import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class P98TrackNotFakePassTests(unittest.TestCase):
    def test_p98_master_gate_is_explicitly_in_progress(self):
        payload = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], "v3.0.1")
        self.assertEqual(payload["track"], "p98_master_gate")
        self.assertEqual(payload["overall_status"], "in_progress")
        self.assertTrue(payload["ecosystem_score_excluded"])
        self.assertEqual(payload["current_stable_line"], "v2.4.1")
        self.assertEqual(payload["p98_track_status"], "development")
        self.assertFalse(payload["final_p98_gate"])
        self.assertIn("not a final P98 pass", payload["current_scope"])

    def test_p95_gate_still_passes_while_p98_is_in_progress(self):
        p95 = json.loads((ROOT / "validation" / "p95_core_triage_gate.json").read_text(encoding="utf-8"))
        p98 = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))

        self.assertEqual(p95["overall_status"], "pass")
        self.assertEqual(p98["overall_status"], "in_progress")
        for pillar in (
            "playwright_trace_doctor",
            "cross_framework_adapters",
            "training_challenge_sedimentation",
            "composite_diagnosis",
            "safety_boundary",
        ):
            self.assertIn(pillar, p95["pillars"])


if __name__ == "__main__":
    unittest.main()
