from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHOWCASE_ROOT = ROOT / "sample_reports" / "composite_showcase"


class CompositeShowcaseReportTests(unittest.TestCase):
    def test_three_sample_reports_expose_composite_chain(self):
        expected = [
            "auth_redirect_plus_selector_timeout",
            "route_har_miss_plus_network_404",
            "antibot_challenge_plus_selector_timeout",
        ]
        for case_id in expected:
            case_dir = SHOWCASE_ROOT / case_id
            self.assertTrue(case_dir.exists(), case_id)
            for filename in (
                "diagnosis.json",
                "diagnosis.md",
                "fix_plan.json",
                "fix_plan.md",
                "verification_report.json",
                "verification_report.md",
                "evidence_graph.json",
            ):
                self.assertTrue((case_dir / filename).exists(), f"{case_id}/{filename}")
            diagnosis = json.loads((case_dir / "diagnosis.json").read_text(encoding="utf-8"))
            for key in ("primary_failure", "secondary_failures", "blocking_failure", "repair_order", "evidence_graph"):
                self.assertIn(key, diagnosis)
            self.assertTrue(diagnosis["repair_order"])
            self.assertTrue(diagnosis["evidence_graph"]["nodes"])


if __name__ == "__main__":
    unittest.main()

