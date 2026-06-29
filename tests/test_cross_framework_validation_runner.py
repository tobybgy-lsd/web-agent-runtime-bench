from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.validation.run_cross_framework_validation import run_validation


class CrossFrameworkValidationRunnerTests(unittest.TestCase):
    def test_runner_covers_40_or_more_cases_with_safe_outputs(self) -> None:
        summary = run_validation()

        self.assertGreaterEqual(summary["total_cases"], 40)
        self.assertGreaterEqual(summary["overall"]["reasonable_category_match"], 35)
        self.assertEqual(summary["overall"]["actionable_next_action"], summary["total_cases"])
        self.assertEqual(summary["overall"]["fix_plan_valid"], summary["total_cases"])
        self.assertEqual(summary["overall"]["forbidden_output_count"], 0)
        self.assertLessEqual(summary["overall"]["severe_misclassification"], 3)
        output = Path("validation/cross_framework_validation.json")
        self.assertTrue(output.exists())
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "v2.2")


if __name__ == "__main__":
    unittest.main()
