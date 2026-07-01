import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VersionAlignmentTests(unittest.TestCase):
    def test_pyproject_readme_and_changelog_align_on_v3_1_0(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        version = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)
        self.assertIsNotNone(version)
        self.assertEqual(version.group(1), "3.6.0")
        self.assertIn("Current milestone: Agent Failure Doctor v3.6 Regulated Industry & Pure Visual Agent Full-Chain Evaluation Pack", readme[:2200])
        self.assertIn("Previous stable line: Agent Failure Doctor v3.5.0", readme[:2200])
        self.assertIn("Current package stable line: v3.6.0", changelog)
        self.assertIn("## v3.3.0", changelog)

    def test_readme_first_screen_explains_p98_and_previous_stable_tracks(self):
        opening = (ROOT / "README.md").read_text(encoding="utf-8")[:2200]

        self.assertIn("Current milestone", opening)
        self.assertIn("v3.6 Regulated Industry & Pure Visual Agent Full-Chain Evaluation Pack", opening)
        self.assertIn("v2.4.1", opening)
        self.assertIn("P98 master gate passed", opening)
        self.assertNotIn("Current milestone: Agent Failure Doctor v3.0.1", opening)


if __name__ == "__main__":
    unittest.main()

