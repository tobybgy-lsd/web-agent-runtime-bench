import unittest

from tools.failure_artifacts.resolution import generate_fix_plan, verify_resolution


class CompositePlanVerifyP95Tests(unittest.TestCase):
    def test_fix_plan_preserves_composite_repair_order(self):
        diagnosis = {
            "failure_type": "playwright_storage_state_context",
            "technical_category": "playwright_storage_state_context",
            "subtype": "login_redirect_after_authenticated_action",
            "repair_order": [
                "Restore authenticated context or session state first.",
                "Re-run and inspect selector or data-shape symptoms only after auth succeeds.",
            ],
            "primary_failure": {"technical_category": "playwright_storage_state_context"},
            "secondary_failures": [{"technical_category": "selector_drift"}],
        }

        plan = generate_fix_plan(diagnosis)

        self.assertEqual(plan["repair_order"], diagnosis["repair_order"])
        self.assertEqual(plan["secondary_failures"][0]["technical_category"], "selector_drift")

    def test_verify_reports_partially_resolved_when_primary_is_fixed_but_secondary_remains(self):
        before = {
            "failure_type": "playwright_storage_state_context",
            "technical_category": "playwright_storage_state_context",
            "evidence": ["302 redirect to login", "selector .price timed out"],
            "secondary_failures": [{"technical_category": "selector_drift"}],
        }
        after = {
            "failure_type": "selector_drift",
            "technical_category": "selector_drift",
            "evidence": ["selector .price timed out"],
        }

        report = verify_resolution(before, {"log": "302 redirect to login selector .price timed out"}, after, {"log": "selector .price timed out"})

        self.assertEqual(report["status"], "partially_resolved")
        self.assertIn("selector_drift", report["new_failures"])


if __name__ == "__main__":
    unittest.main()

