import unittest

from tools.failure_artifacts.candidates import collect_diagnosis_candidates
from tools.failure_artifacts.composite import classify_composite_failure_artifact
from tools.failure_artifacts.evidence_graph import build_evidence_graph
from tools.failure_artifacts.evidence_nodes import extract_evidence_nodes


def artifact(message: str, observations=None, status_code=200):
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": "composite_p95_test",
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": "composite diagnosis test",
        "error": {"message": message, "stack": "", "status_code": status_code},
        "artifacts": {},
        "observations": observations or {},
        "expected": {"required_fields": []},
        "actual": {"fields": {}, "array_length": None},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {
            "sanitized": True,
            "contains_credentials": False,
            "external_network_required": False,
            "user_authorized_or_synthetic": True,
        },
    }


class CompositeP95EngineTests(unittest.TestCase):
    def test_auth_redirect_and_selector_timeout_become_composite_with_auth_first(self):
        sample = artifact(
            "locator.click: Timeout waiting for selector .price",
            {
                "auth_redirect_detected": True,
                "redirected_to_login": True,
                "auth_status_code": 302,
                "final_url": "https://example.test/login",
                "missing_selectors": [".price"],
                "network_events": [{"status": 302, "url": "https://example.test/login"}],
            },
            status_code=302,
        )

        candidates = collect_diagnosis_candidates(sample)
        self.assertIn("playwright_storage_state_context", {item["technical_category"] for item in candidates})
        self.assertIn("selector_drift", {item["technical_category"] for item in candidates})
        self.assertTrue(all(item["evidence_ids"] for item in candidates))

        diagnosis = classify_composite_failure_artifact(sample)
        self.assertEqual(diagnosis["diagnosis_mode"], "composite")
        self.assertEqual(diagnosis["primary_failure"]["technical_category"], "playwright_storage_state_context")
        self.assertEqual(diagnosis["blocking_failure"]["technical_category"], "playwright_storage_state_context")
        self.assertIn("selector", diagnosis["downstream_failures"][0]["technical_category"])
        self.assertIn("auth", " ".join(diagnosis["repair_order"]).lower())
        self.assertIn("selector", " ".join(diagnosis["repair_order"]).lower())
        self.assertEqual(diagnosis["failure_type"], "playwright_storage_state_context")

    def test_antibot_boundary_blocks_downstream_selector_without_bypass_text(self):
        sample = artifact(
            "HTTP 429 too many requests; locator .submit timed out after challenge page",
            {
                "body_text": "Verify you are human before continuing",
                "missing_selectors": [".submit"],
                "network_events": [{"status": 429, "url": "https://example.test/products"}],
            },
            status_code=429,
        )
        diagnosis = classify_composite_failure_artifact(sample)
        combined = str(diagnosis).lower()

        self.assertEqual(diagnosis["primary_failure"]["technical_category"], "anti_bot_risk")
        self.assertEqual(diagnosis["blocking_failure"]["technical_category"], "anti_bot_risk")
        self.assertTrue(diagnosis["safe_next_action"])
        for forbidden in ("captcha bypass", "bot evasion", "fingerprint spoofing", "dynamic signature cracking"):
            self.assertNotIn(forbidden, combined)

    def test_evidence_graph_links_route_miss_to_network_error(self):
        sample = artifact(
            "routeFromHAR failed: HAR not found; live request returned 404",
            {
                "har_expected": True,
                "har_loaded": False,
                "har_error": "HAR not found",
                "network_events": [{"status": 404, "url": "https://example.test/api/products"}],
            },
            status_code=404,
        )
        nodes = extract_evidence_nodes(sample)
        candidates = collect_diagnosis_candidates(sample)
        graph = build_evidence_graph(nodes, candidates)
        relations = {edge["relation"] for edge in graph["edges"]}

        self.assertIn("likely_causes", relations)
        diagnosis = classify_composite_failure_artifact(sample)
        self.assertEqual(diagnosis["primary_failure"]["technical_category"], "playwright_route_mock_har")
        self.assertIn("network_http_error", {item["technical_category"] for item in diagnosis["secondary_failures"]})

    def test_only_user_description_becomes_insufficient_evidence(self):
        sample = artifact("", {"user_description": "Maybe the proxy failed and maybe the selector changed."})
        diagnosis = classify_composite_failure_artifact(sample)

        self.assertEqual(diagnosis["primary_failure"]["technical_category"], "insufficient_evidence")
        self.assertLessEqual(diagnosis["primary_failure"]["confidence"], 0.65)
        self.assertEqual(diagnosis["diagnosis_mode"], "single")


if __name__ == "__main__":
    unittest.main()

