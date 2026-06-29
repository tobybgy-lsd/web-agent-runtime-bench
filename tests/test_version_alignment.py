import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VersionAlignmentTests(unittest.TestCase):
    def test_pyproject_readme_and_changelog_align_on_v3_0_1(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        version = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)
        self.assertIsNotNone(version)
        self.assertEqual(version.group(1), "3.0.1")
        self.assertIn("Current milestone: Agent Failure Doctor v3.0.1", readme[:2200])
        self.assertIn("## v3.0.1", changelog)

    def test_readme_first_screen_does_not_mix_old_stable_milestones(self):
        opening = (ROOT / "README.md").read_text(encoding="utf-8")[:2200]

        self.assertNotIn("Current stable milestone", opening)
        self.assertNotIn("v2.4.1", opening)
        self.assertIn("P98 is in progress, not a final passed master gate", opening)


if __name__ == "__main__":
    unittest.main()
