import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VersionAlignmentTests(unittest.TestCase):
    def test_pyproject_readme_and_changelog_align_on_stable_v2_4_1(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        version = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)
        self.assertIsNotNone(version)
        self.assertEqual(version.group(1), "2.4.1")
        self.assertIn("Current stable milestone: Agent Failure Doctor v2.4.1", readme[:2200])
        self.assertIn("Development track: v3.0.x P98 Controlled Maturity Pack", readme[:2200])
        self.assertIn("Current package stable line: v2.4.1", changelog)
        self.assertIn("v3.0.x entries document the in-progress P98 development track", changelog)
        self.assertIn("## v3.0.1", changelog)

    def test_readme_first_screen_explains_stable_and_development_tracks(self):
        opening = (ROOT / "README.md").read_text(encoding="utf-8")[:2200]

        self.assertIn("Current stable milestone", opening)
        self.assertIn("v2.4.1", opening)
        self.assertIn("P98 is in progress, not the current packaged stable release", opening)
        self.assertNotIn("Current milestone: Agent Failure Doctor v3.0.1", opening)


if __name__ == "__main__":
    unittest.main()
