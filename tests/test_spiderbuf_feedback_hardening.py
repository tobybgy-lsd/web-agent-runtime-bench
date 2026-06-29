import json
import unittest

from tools.failure_artifacts.classifier import classify_failure_artifact
from tools.failure_artifacts.composite import classify_composite_failure_artifact
from tools.failure_artifacts.guardrails import forbidden_output_hits


def artifact(message: str, observations=None, status_code=200):
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": "spiderbuf_feedback_hardening",
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": "Spiderbuf-inspired hardening regression",
        "error": {"message": message, "stack": "", "status_code": status_code},
        "artifacts": {},
        "observations": observations or {},
        "expected": {"required_fields": ["title", "price"]},
        "actual": {"fields": {}, "array_length": None},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {
            "sanitized": True,
            "contains_credentials": False,
            "external_network_required": False,
            "user_authorized_or_synthetic": True,
        },
    }


class SpiderbufFeedbackHardeningTests(unittest.TestCase):
    def test_local_exception_bias_outranks_html_and_selector_noise(self):
        sample = artifact(
            "FileNotFoundError: [Errno 2] No such file or directory: './data/e03/e03_1.html'",
            {
                "log_excerpt": (
                    "FileNotFoundError: [Errno 2] No such file or directory: './data/e03/e03_1.html'\n"
                    "<html><div class='product'>price selector empty</div><script>selector not found</script></html>"
                ),
                "html_excerpt": "<main>new layout selector not found</main>",
            },
        )

        diagnosis = classify_failure_artifact(sample)

        self.assertEqual(diagnosis["failure_type"], "toolchain_environment")
        self.assertEqual(diagnosis["subtype"], "local_file_path_missing")
        self.assertGreaterEqual(diagnosis["confidence"], 0.9)

    def test_download_saveas_enoent_stays_download_diagnosis(self):
        sample = artifact("download.saveAs failed with ENOENT: no such file or directory: './downloads/report.csv'")

        diagnosis = classify_failure_artifact(sample)

        self.assertEqual(diagnosis["failure_type"], "playwright_download")

    def test_antibot_primary_suppresses_downstream_selector_symptom(self):
        sample = artifact(
            "HTTP 429 too many requests; locator.click: Timeout waiting for selector .price",
            {
                "body_text": "Verify you are human before continuing",
                "network_events": [{"status": 429, "url": "https://example.test/products"}],
                "missing_selectors": [".price"],
            },
            status_code=429,
        )

        diagnosis = classify_composite_failure_artifact(sample)
        suppressed = [
            item
            for item in diagnosis["secondary_failures"]
            if item["technical_category"] in {"selector_drift", "website_change", "response_shape_change"}
        ]

        self.assertEqual(diagnosis["primary_failure"]["technical_category"], "anti_bot_risk")
        self.assertTrue(suppressed)
        self.assertTrue(all(item.get("suppressed_by_primary") for item in suppressed))
        self.assertTrue(any(item.get("relationship_to_primary") == "suppressed_downstream" for item in suppressed))

    def test_dynamic_signature_guidance_is_safe_linter_style(self):
        sample = artifact("request failed because signature token x-bogus is invalid")

        diagnosis = classify_failure_artifact(sample)
        combined = json.dumps(diagnosis, ensure_ascii=False).lower()

        self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
        self.assertEqual(diagnosis["subtype"], "dynamic_signature_required")
        self.assertIn("official api", combined)
        self.assertIn("local clock", combined)
        self.assertIn("parameter ordering", combined)
        self.assertFalse(forbidden_output_hits(combined))

    def test_guardrails_catch_expanded_evasion_terms(self):
        text = "Try webdriver stealth with canvas spoofing and residential proxy rotation."

        hits = forbidden_output_hits(text)

        self.assertIn("webdriver stealth", hits)
        self.assertIn("canvas spoofing", hits)
        self.assertIn("residential proxy rotation", hits)


if __name__ == "__main__":
    unittest.main()
