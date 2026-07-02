from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DashboardP95TrackTests(unittest.TestCase):
    def test_dashboard_lists_all_alignment_tracks(self):
        text = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        required = [
            "Template fixtures",
            "Public-inspired independent set",
            "Real Playwright trace semantic fixtures",
            "Website-change / anti-bot routing",
            "External public reference validation",
            "Resolution validation",
            "Applied scenario validation",
            "Cross-framework adapter validation",
            "Spiderbuf-inspired validation",
            "Training challenge P95 validation",
            "Playwright Trace Doctor P95 validation",
            "Composite Diagnosis P95 Strict",
            "P95 Core Triad Gate",
        ]
        for label in required:
            self.assertIn(label, text)


if __name__ == "__main__":
    unittest.main()

