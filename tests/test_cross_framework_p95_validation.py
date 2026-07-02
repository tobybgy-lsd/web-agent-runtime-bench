from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CrossFrameworkP95ValidationTests(unittest.TestCase):
    def test_cross_framework_p95_runner_meets_thresholds(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_cross_framework_p95_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads((ROOT / "validation" / "cross_framework_p95_validation.json").read_text(encoding="utf-8"))
        counts = data["framework_counts"]

        self.assertGreaterEqual(data["total_cases"], 100)
        self.assertGreaterEqual(counts["selenium"], 25)
        self.assertGreaterEqual(counts["puppeteer"], 25)
        self.assertGreaterEqual(counts["cypress"], 20)
        self.assertGreaterEqual(counts["scrapy"] + counts["requests"] + counts["httpx"], 20)
        self.assertGreaterEqual(counts["browser_use"] + counts["generic_rpa"], 10)
        self.assertGreaterEqual(data["reasonable"], 90)
        self.assertEqual(data["actionable"], data["total_cases"])
        self.assertGreaterEqual(data["fix_plan_valid"], 95)
        self.assertEqual(data["forbidden_output_count"], 0)
        self.assertEqual(data["status"], "pass")


if __name__ == "__main__":
    unittest.main()

