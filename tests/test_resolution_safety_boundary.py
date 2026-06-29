import unittest

from tools.failure_artifacts.resolution import FORBIDDEN_RESOLUTION_TERMS, generate_fix_plan, render_verification_markdown, verify_resolution


class ResolutionSafetyBoundaryTests(unittest.TestCase):
    def test_anti_bot_plan_and_verification_do_not_emit_forbidden_terms(self):
        diagnosis = {"failure_type": "anti_bot_risk", "subtype": "captcha_or_challenge_page", "evidence": ["challenge marker found"]}
        plan = generate_fix_plan(diagnosis)
        report = verify_resolution(diagnosis, {}, {"failure_type": "none_detected", "evidence": ["official API used"]}, {}, plan)
        combined = (str(plan) + render_verification_markdown(report)).lower()
        for term in FORBIDDEN_RESOLUTION_TERMS:
            self.assertNotIn(term.lower(), combined)
        self.assertNotEqual(report["status"], "resolved")


if __name__ == "__main__":
    unittest.main()
