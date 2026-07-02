import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class KnowledgeBasePatternTests(unittest.TestCase):
    def test_knowledge_base_contains_120_valid_patterns(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.knowledge_base.validate_patterns"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreaterEqual(payload["total_patterns"], 120)
        self.assertEqual(payload["forbidden_output_count"], 0)
        self.assertGreaterEqual(payload["anti_bot_patterns"], 15)

    def test_knowledge_base_search_finds_selector_and_selenium_patterns(self):
        selector = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.knowledge_base.search_patterns",
                "--query",
                "selector_drift",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        selenium = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.knowledge_base.search_patterns",
                "--query",
                "Selenium NoSuchElementException",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(selector.returncode, 0, selector.stdout + selector.stderr)
        self.assertEqual(selenium.returncode, 0, selenium.stdout + selenium.stderr)
        self.assertIn("selector_drift", selector.stdout)
        self.assertIn("selenium", selenium.stdout.lower())
        self.assertIn("no_such_element", selenium.stdout.lower())


if __name__ == "__main__":
    unittest.main()

