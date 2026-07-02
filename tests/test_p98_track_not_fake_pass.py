import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class P98TrackNotFakePassTests(unittest.TestCase):
    def test_p98_master_gate_is_explicitly_final_and_evidence_backed(self):
        payload = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], "v3.9.0")
        self.assertEqual(payload["overall_status"], "pass")
        self.assertTrue(payload["final_p98_gate"])
        self.assertTrue(payload["ecosystem_score_excluded"])
        self.assertGreaterEqual(payload["controlled_maturity_score"], 98)
        self.assertEqual(payload["current_stable_line"], "v3.9.0")
        self.assertEqual(payload["previous_stable_line"], "v3.8.0")
        self.assertEqual(payload["global_forbidden_output_count"], 0)
        self.assertEqual(payload["global_private_solution_leak_count"], 0)
        self.assertEqual(payload["global_real_platform_access_count"], 0)
        self.assertEqual(payload["blocking_failures"], [])

    def test_p95_gate_still_passes_under_final_p98_gate(self):
        p95 = json.loads((ROOT / "validation" / "p95_core_triage_gate.json").read_text(encoding="utf-8"))
        p98 = json.loads((ROOT / "validation" / "p98_master_gate.json").read_text(encoding="utf-8"))

        self.assertEqual(p95["overall_status"], "pass")
        self.assertEqual(p98["overall_status"], "pass")
        for pillar in (
            "knowledge_base",
            "crawler_coverage_matrix",
            "playwright_trace_doctor",
            "cross_framework_adapter",
            "training_challenge_sedimentation",
            "composite_counterfactual_diagnosis",
            "ai_handoff_patch_proposal",
            "batch_fleet_diagnosis",
            "sanitize_share_pack",
            "safety_boundary",
        ):
            self.assertIn(pillar, p98["pillars"])
            self.assertEqual(p98["pillars"][pillar]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
