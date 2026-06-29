from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PlaywrightTraceP95ValidationTests(unittest.TestCase):
    def test_playwright_trace_p95_runner_meets_thresholds(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_playwright_trace_p95_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads((ROOT / "validation" / "playwright_trace_p95_validation.json").read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["native_playwright_trace_fixtures"], 100)
        self.assertFalse(data["uses_custom_classifier_fields"])
        self.assertGreaterEqual(data["reasonable"], 92)
        self.assertGreaterEqual(data["exact_subtype"], 88)
        self.assertGreaterEqual(data["actionable"], 95)
        self.assertLessEqual(data["severe_misclassification"], 4)
        self.assertEqual(data["forbidden_output_count"], 0)
        self.assertEqual(data["status"], "pass")


if __name__ == "__main__":
    unittest.main()
