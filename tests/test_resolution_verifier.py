import unittest

from tools.failure_artifacts.resolution import generate_fix_plan, verify_resolution


def diag(failure_type, subtype="", evidence=None):
    return {
        "failure_type": failure_type,
        "technical_category": failure_type,
        "subtype": subtype,
        "evidence": evidence or [],
        "confidence": 0.9,
    }


class ResolutionVerifierTests(unittest.TestCase):
    def test_selector_drift_resolved(self):
        before = diag("selector_drift", "missing_selector", ["missing selector .price", "locator resolved to 0 elements"])
        after = diag("none_detected", "", ["selector .amount matched", "price field extracted"])
        report = verify_resolution(before, {}, after, {}, generate_fix_plan(before))
        self.assertEqual(report["status"], "resolved")
        self.assertTrue(report["resolved_evidence"])

    def test_selector_drift_not_resolved(self):
        before = diag("selector_drift", "missing_selector", ["missing selector .price"])
        after = diag("selector_drift", "missing_selector", ["missing selector .price"])
        report = verify_resolution(before, {}, after, {}, generate_fix_plan(before))
        self.assertEqual(report["status"], "not_resolved")
        self.assertTrue(report["remaining_evidence"])

    def test_changed_failure(self):
        before = diag("selector_drift", "missing_selector", ["missing selector .price"])
        after = diag("playwright_storage_state_context", "login_redirect", ["302 redirect to login"])
        report = verify_resolution(before, {}, after, {}, generate_fix_plan(before))
        self.assertEqual(report["status"], "changed_failure")
        self.assertIn("playwright_storage_state_context", report["new_failures"])

    def test_anti_bot_does_not_claim_bypass_resolved(self):
        before = diag("anti_bot_risk", "captcha_or_challenge_page", ["challenge marker found"])
        after = diag("none_detected", "", ["challenge no longer visible"])
        report = verify_resolution(before, {}, after, {}, generate_fix_plan(before))
        self.assertEqual(report["status"], "insufficient_evidence")
        self.assertIn("compliant", " ".join(report["notes"]).lower())


if __name__ == "__main__":
    unittest.main()

