import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class P98PillarValidationTests(unittest.TestCase):
    def _run(self, module: str, filename: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", module],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads((ROOT / "validation" / filename).read_text(encoding="utf-8"))

    def test_playwright_trace_p98_validation(self):
        payload = self._run(
            "tools.validation.run_playwright_trace_p98_validation",
            "playwright_trace_p98_validation.json",
        )
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 220)
        self.assertEqual(payload["synthetic_classifier_fields_present"], 0)
        self.assertEqual(payload["forbidden_output_count"], 0)

    def test_cross_framework_p98_validation(self):
        payload = self._run(
            "tools.validation.run_cross_framework_p98_validation",
            "cross_framework_p98_validation.json",
        )
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 240)
        self.assertEqual(payload["actionable_next_action"], 240)

    def test_training_composite_handoff_batch_sanitize_p98_validations(self):
        modules = {
            "tools.validation.run_training_challenge_p98_validation": "training_challenge_p98_validation.json",
            "tools.validation.run_composite_counterfactual_p98_validation": "composite_counterfactual_p98_validation.json",
            "tools.validation.run_ai_handoff_p98_validation": "ai_handoff_p98_validation.json",
            "tools.validation.run_batch_diagnosis_p98_validation": "batch_diagnosis_p98_validation.json",
            "tools.validation.run_sanitize_share_p98_validation": "sanitize_share_p98_validation.json",
        }
        for module, filename in modules.items():
            with self.subTest(module=module):
                payload = self._run(module, filename)
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["forbidden_output_count"], 0)
                self.assertEqual(payload["private_solution_leak_count"], 0)
                self.assertEqual(payload["real_platform_access_count"], 0)


if __name__ == "__main__":
    unittest.main()
