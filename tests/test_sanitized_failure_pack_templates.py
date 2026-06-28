import unittest
from pathlib import Path

from tools.failure_artifacts.artifact import load_artifact, validate_artifact
from tools.failure_artifacts.diagnose import diagnose_artifact


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "examples" / "sanitized_failure_packs"


class SanitizedFailurePackTemplateTests(unittest.TestCase):
    def test_realistic_sanitized_templates_are_valid_and_diagnosable(self):
        expected_types = {
            "playwright_selector_drift_product_card": "selector_drift",
            "playwright_auth_expired_login_page": "auth_expiry",
            "scrapy_rate_limit_soft_block": "anti_bot_risk",
            "playwright_navigation_timeout": "network_http_error",
            "playwright_async_hydration_product_grid": "async_hydration_timing",
            "playwright_captcha_challenge_wall": "anti_bot_risk",
            "node_runtime_document_missing": "runtime_api_missing",
            "api_response_shape_changed": "website_change",
            "playwright_js_bundle_obfuscation": "js_bundle_obfuscation",
            "playwright_strict_mode_violation": "playwright_strict_mode_violation",
            "playwright_frame_locator_missing": "playwright_frame_locator",
            "playwright_file_chooser_upload": "playwright_file_chooser",
            "playwright_download_failure": "playwright_download",
            "playwright_popup_new_page": "playwright_popup",
            "playwright_service_worker_cache_stale": "playwright_service_worker_cache",
            "playwright_storage_cookie_domain_mismatch": "playwright_storage_state_context",
            "playwright_storage_state_not_loaded": "playwright_storage_state_context",
            "playwright_context_recreated_without_state": "playwright_storage_state_context",
            "playwright_storage_local_storage_missing": "playwright_storage_state_context",
            "playwright_storage_base_url_origin_mismatch": "playwright_storage_state_context",
            "playwright_route_pattern_mismatch": "playwright_route_mock_har",
            "playwright_route_registered_too_late": "playwright_route_mock_har",
            "playwright_har_not_loaded": "playwright_route_mock_har",
            "playwright_har_fallback_network_leak": "playwright_route_mock_har",
            "playwright_mock_response_shape_mismatch": "playwright_route_mock_har",
            "playwright_shadow_root_boundary": "playwright_shadow_dom_locator",
            "playwright_closed_shadow_root_unreachable": "playwright_shadow_dom_locator",
            "playwright_custom_element_not_upgraded": "playwright_shadow_dom_locator",
            "playwright_shadow_host_not_inner_node": "playwright_shadow_dom_locator",
            "playwright_testid_inside_shadow_dom_missing_strategy": "playwright_shadow_dom_locator",
        }
        expected_subtypes = {
            "playwright_storage_cookie_domain_mismatch": "cookie_domain_mismatch",
            "playwright_storage_state_not_loaded": "storage_state_not_loaded",
            "playwright_context_recreated_without_state": "context_recreated_without_state",
            "playwright_storage_local_storage_missing": "local_storage_missing",
            "playwright_storage_base_url_origin_mismatch": "base_url_state_origin_mismatch",
            "playwright_route_pattern_mismatch": "route_pattern_mismatch",
            "playwright_route_registered_too_late": "route_registered_too_late",
            "playwright_har_not_loaded": "har_not_found_or_not_loaded",
            "playwright_har_fallback_network_leak": "har_fallback_network_leak",
            "playwright_mock_response_shape_mismatch": "mock_response_shape_mismatch",
            "playwright_shadow_root_boundary": "shadow_root_boundary",
            "playwright_closed_shadow_root_unreachable": "closed_shadow_root_unreachable",
            "playwright_custom_element_not_upgraded": "custom_element_not_upgraded",
            "playwright_shadow_host_not_inner_node": "locator_targets_host_not_inner_node",
            "playwright_testid_inside_shadow_dom_missing_strategy": "testid_inside_shadow_dom_missing_strategy",
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
                if case_name in expected_subtypes:
                    self.assertEqual(diagnosis["subtype"], expected_subtypes[case_name])
                self.assertGreaterEqual(diagnosis["confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
