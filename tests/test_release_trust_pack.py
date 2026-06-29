import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseTrustPackTests(unittest.TestCase):
    def test_versions_and_readme_validation_milestone_are_aligned(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        dashboard = (ROOT / "validation" / "dashboard.md").read_text(encoding="utf-8")
        self.assertIn('version = "2.5.0"', pyproject)
        self.assertIn("## v2.1.0", changelog)
        self.assertIn("## v2.0.0", changelog)
        self.assertIn("v2.5.0 AI Handoff & Patch Proposal Pack", readme)
        self.assertIn("v2.0 Auto Capture", readme)
        self.assertIn("62 external public reference seeds", readme)
        self.assertIn("External held-out public-source set", dashboard)

    def test_readme_top_is_not_redundant_or_mojibake(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        top = readme[:1200]
        self.assertIn("Local-first failure diagnosis", top)
        self.assertIn("trace.zip / error.log / console.txt / network.json / screenshot metadata / user_description.txt", top)
        self.assertIn("diagnosis, evidence, next action, repair suggestions, GitHub issue draft, Codex fix prompt.", top)
        self.assertEqual(top.count("diagnosis, evidence, next action"), 1)
        self.assertNotIn("娑", top)
        self.assertNotIn("閺", top)

    def test_external_heldout_validation_is_reproducible(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_external_heldout.py"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads((ROOT / "validation" / "external_heldout_10.json").read_text(encoding="utf-8"))
        summary = data["summary"]
        self.assertEqual(summary["sample_count"], 10)
        self.assertGreaterEqual(summary["reasonable_classifications"], 7)
        self.assertGreaterEqual(summary["actionable_next_actions"], 8)
        self.assertEqual(summary["forbidden_outputs"], 0)

