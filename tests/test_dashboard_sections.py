import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DashboardSectionTests(unittest.TestCase):
    def test_dashboard_separates_stable_p95_and_final_p98_tracks(self):
        text = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")

        for heading in (
            "## 1. Current Stable Release",
            "## 2. P95 Completed Gates",
            "## 3. P98 Master Gate",
            "## 4. Limits",
        ):
            self.assertIn(heading, text)

    def test_dashboard_tracks_have_status_reproduce_and_forbidden_output(self):
        text = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        required_tracks = (
            "Agent Failure Doctor v5.1.0",
            "Playwright Trace P95",
            "Cross-framework P95",
            "Training Challenge P95",
            "Knowledge Base P98",
            "Playwright Trace P98",
            "Cross-framework P98",
            "Training Challenge P98",
            "Composite + Counterfactual P98",
            "AI Handoff P98",
            "Batch / Fleet P98",
            "Sanitize / Share P98",
            "P98 Master Gate",
        )
        for track in required_tracks:
            self.assertIn(track, text)
        self.assertIn("Reproduce", text)
        self.assertRegex(text, r"Forbidden Output")
        self.assertTrue(all(value == "0" for value in re.findall(r"\|\s*(\d+)\s*\|\s*pass\s*\|", text)))


if __name__ == "__main__":
    unittest.main()

