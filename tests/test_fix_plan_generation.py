import unittest

from tools.failure_artifacts.resolution import FORBIDDEN_RESOLUTION_TERMS, generate_fix_plan


class FixPlanGenerationTests(unittest.TestCase):
    def test_core_failure_types_generate_fix_plans(self):
        failure_types = (
            "selector_drift",
            "playwright_storage_state_context",
            "playwright_route_mock_har",
            "playwright_shadow_dom_locator",
            "playwright_strict_mode_violation",
            "playwright_download",
            "playwright_popup",
            "playwright_execution_context_destroyed",
            "network_http_error",
            "website_change",
            "anti_bot_risk",
            "insufficient_evidence",
        )
        for failure_type in failure_types:
            with self.subTest(failure_type=failure_type):
                plan = generate_fix_plan({"failure_type": failure_type, "subtype": "sample", "evidence": ["missing selector .price"]})
                self.assertEqual(plan["schema_version"], "fix_plan/v1")
                self.assertEqual(plan["failure_type"], failure_type)
                self.assertTrue(plan["fix_intent"])
                self.assertTrue(plan["expected_evidence_to_appear"])
                self.assertIn(plan["risk"], {"low", "medium", "high"})

    def test_anti_bot_plan_is_compliance_only(self):
        plan = generate_fix_plan({"failure_type": "anti_bot_risk", "subtype": "captcha_or_challenge_page", "evidence": ["captcha"]})
        combined = " ".join(str(value) for value in plan.values()).lower()
        for term in FORBIDDEN_RESOLUTION_TERMS:
            self.assertNotIn(term.lower(), combined)
        self.assertIn("official API", " ".join(plan["expected_evidence_to_appear"]))
        self.assertTrue(plan["safe_next_action"])

    def test_insufficient_evidence_plan_requests_more_artifacts(self):
        plan = generate_fix_plan({"failure_type": "insufficient_evidence", "evidence": []})
        self.assertIn("trace.zip", plan["expected_evidence_to_appear"])
        self.assertIn("error.log", plan["expected_evidence_to_appear"])
        self.assertEqual(plan["risk"], "low")


if __name__ == "__main__":
    unittest.main()

