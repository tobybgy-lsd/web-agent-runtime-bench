import unittest
from pathlib import Path

from tools.failure_artifacts.artifact import load_artifact, validate_artifact
from tools.failure_artifacts.diagnose import diagnose_artifact


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "examples" / "sanitized_failure_packs"


class SanitizedFailurePackTemplateTests(unittest.TestCase):
    def test_three_realistic_sanitized_templates_are_valid_and_diagnosable(self):
        expected_types = {
            "playwright_selector_drift_product_card": "selector_drift",
            "playwright_auth_expired_login_page": "auth_expiry",
            "scrapy_rate_limit_soft_block": "rate_limit_or_soft_block",
        }

        for case_name, expected_type in expected_types.items():
            with self.subTest(case=case_name):
                case_dir = TEMPLATE_ROOT / case_name
                artifact_path = case_dir / "failure_artifact.json"

                self.assertTrue(artifact_path.exists(), msg=f"missing {artifact_path}")
                artifact = load_artifact(artifact_path)

                self.assertEqual(validate_artifact(artifact, base_dir=case_dir), [])
                self.assertTrue((case_dir / "README.md").exists())
                self.assertTrue(artifact["safety"]["sanitized"])
                self.assertFalse(artifact["safety"]["contains_credentials"])
                self.assertFalse(artifact["safety"]["external_network_required"])

                for rel_path in artifact["artifacts"].values():
                    if rel_path:
                        self.assertTrue((case_dir / rel_path).exists(), msg=f"missing referenced artifact: {rel_path}")

                diagnosis = diagnose_artifact(artifact)
                self.assertEqual(diagnosis["failure_type"], expected_type)
                self.assertGreaterEqual(diagnosis["confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
