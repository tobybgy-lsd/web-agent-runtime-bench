import unittest

from tools.failure_artifacts.regression_case import create_regression_case


class RegressionCaseGenerationTests(unittest.TestCase):
    def test_regression_case_defaults_to_private(self):
        report = {
            "status": "resolved",
            "before": {"failure_type": "selector_drift", "subtype": "missing_selector"},
            "after": {"failure_type": "none_detected", "subtype": ""},
        }
        case = create_regression_case("before", "after", report)
        self.assertEqual(case["source"], "verification_loop")
        self.assertFalse(case["safe_to_publish"])
        self.assertEqual(case["before_failure_type"], "selector_drift")


if __name__ == "__main__":
    unittest.main()

