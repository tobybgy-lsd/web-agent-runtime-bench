import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "validation" / "real_trace_validation_30.json"


class RealTraceValidationRunnerTests(unittest.TestCase):
    def test_real_trace_validation_runner_writes_required_metrics(self):
        completed = subprocess.run(
            [sys.executable, "-m", "tools.validation.run_real_trace_validation"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(RESULT.exists())
        data = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(data["track"], "real_playwright_trace_semantic_validation")
        self.assertGreaterEqual(data["total_cases"], 30)
        self.assertGreaterEqual(data["reasonable_category_match"], 26)
        self.assertGreaterEqual(data["exact_subtype_match"], 22)
        self.assertGreaterEqual(data["actionable_next_action"], 27)
        self.assertLessEqual(data["severe_misclassification"], 2)
        self.assertEqual(data["forbidden_output_count"], 0)
        self.assertGreaterEqual(len(data["cases"]), 30)

