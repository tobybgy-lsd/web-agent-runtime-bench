from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TrainingChallengeP95ValidationTests(unittest.TestCase):
    def test_training_challenge_runner_meets_thresholds(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_training_challenge_validation"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads((ROOT / "validation" / "training_challenge_p95_validation.json").read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["total_cases"], 40)
        self.assertGreaterEqual(data["challenge_counts"]["spiderbuf_inspired"], 20)
        self.assertGreaterEqual(data["challenge_counts"]["generic_crawler_training"], 20)
        self.assertGreaterEqual(data["diagnosis_reasonable"], 38)
        self.assertEqual(data["fix_plan_valid"], data["total_cases"])
        self.assertGreaterEqual(data["verification_correct"], 36)
        self.assertEqual(data["forbidden_output_count"], 0)
        self.assertEqual(data["private_solution_leak_count"], 0)
        self.assertEqual(data["status"], "pass")


if __name__ == "__main__":
    unittest.main()

