import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ValidationDashboardTracksTests(unittest.TestCase):
    def test_dashboard_shows_three_honest_validation_tracks(self):
        text = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        self.assertIn("Template fixtures", text)
        self.assertIn("Public-inspired independent set", text)
        self.assertIn("Real Playwright trace semantic fixtures", text)
        self.assertIn("External held-out public-source set", text)
        self.assertIn("97.3%", text)
        self.assertIn("78.0%", text)
        self.assertIn("90.0%", text)
        self.assertRegex(text, r"Forbidden Output|forbidden output")
        self.assertNotIn("all samples are real public traces", text.lower())
