import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CompositeP95ScorecardTests(unittest.TestCase):
    def test_scorecard_defines_strict_global_and_family_gates(self):
        scorecard = ROOT / "docs" / "COMPOSITE_DIAGNOSIS_P95_SCORECARD.md"
        self.assertTrue(scorecard.exists())
        text = scorecard.read_text(encoding="utf-8")

        for required in (
            "Global Gate",
            "Per-Family Gate",
            "114/120",
            "19/20",
            "forbidden_output = 0",
            "overconfident_wrong",
            "auth_selector_composites",
            "route_har_network_composites",
            "antibot_downstream_composites",
            "network_environment_navigation_composites",
            "dom_frame_shadow_selector_composites",
            "website_change_business_logic_composites",
        ):
            self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
