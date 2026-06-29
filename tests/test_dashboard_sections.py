import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DashboardSectionTests(unittest.TestCase):
    def test_dashboard_separates_stable_p95_and_p98_tracks(self):
        text = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")

        for heading in (
            "## A. Stable Core Tracks",
            "## B. P95 Completed Gates",
            "## C. P98 Development Tracks",
        ):
            self.assertIn(heading, text)

    def test_dashboard_tracks_have_status_reproduce_and_forbidden_output(self):
        text = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        required_tracks = (
            "Template fixtures",
            "Real Playwright trace semantic fixtures",
            "Playwright Trace Doctor P95 validation",
            "Cross-framework P95 validation",
            "Training challenge P95 validation",
            "Composite Diagnosis P95 Strict",
            "AI Handoff & Patch Proposal",
            "Batch Diagnosis / Fleet Mode",
            "P98 Controlled Maturity Skeleton",
            "Future P98 Master Gate",
        )
        for track in required_tracks:
            self.assertIn(track, text)
        self.assertIn("Reproduce Command", text)
        self.assertRegex(text, r"Forbidden Output")
        self.assertTrue(all(value == "0" for value in re.findall(r"\|\s*(\d+)\s*\|\s*(?:pass|in_progress)\s*\|", text)))


if __name__ == "__main__":
    unittest.main()
