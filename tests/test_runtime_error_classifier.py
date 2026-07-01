import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "demo" / "phase5_2_runtime"))

from runtime_error_classifier import classify_runtime_error, classify_scraper_error


class RuntimeErrorClassifierTests(unittest.TestCase):
    def test_local_storage_get_item_type_error_is_classified_as_missing_local_storage(self):
        stderr = """
TypeError: Cannot read properties of undefined (reading 'getItem')
    at bundle_local_storage_required.js:5
  var salt = _ls.getItem("warb_demo_salt") || "synthetic_salt_v1";
"""

        result = classify_runtime_error(stderr)

        self.assertEqual(result["error_type"], "missing_local_storage")
        self.assertGreaterEqual(result["confidence"], 0.8)

    def test_missing_required_headers_beats_crypto_keyword_noise(self):
        stderr = """
HTTP 400 Bad Request
Missing required headers: X-Timestamp, X-Nonce, X-Sign
debug context mentions xorResult from page script
"""

        result = classify_scraper_error(stderr)

        self.assertEqual(result["error_type"], "signature_param_missing")
        self.assertGreaterEqual(result["confidence"], 0.85)

    def test_js_challenge_page_is_detected_from_503_html(self):
        html = """
<html><title>Just a moment...</title>
<script>
setTimeout(function() {
  document.cookie = "clearance=" + md5("clearance_challenge_salt_" + bucket);
  location.reload();
}, 1500);
</script></html>
"""

        result = classify_scraper_error("HTTP 503 Service Unavailable", html=html)

        self.assertEqual(result["error_type"], "challenge_page_detected")
        self.assertGreaterEqual(result["confidence"], 0.9)

    def test_tailwind_classes_do_not_trigger_random_css(self):
        html = """
<div class="border hidden sticky shadow rounded flex grid inline table object static relative absolute select">
  <button class="rounded shadow border">Submit</button>
</div>
"""

        result = classify_scraper_error("extraction returned empty", html=html)

        self.assertNotEqual(result["error_type"], "css_random_class")

    def test_browser_fingerprint_signal_is_classified_without_evasion_steps(self):
        stderr = """
HTTP 403 Forbidden
browser fingerprint check failed: navigator.webdriver=true and headless chrome mismatch
"""

        result = classify_scraper_error(stderr)

        self.assertEqual(result["error_type"], "fingerprint_detected")
        self.assertGreaterEqual(result["confidence"], 0.85)
        self.assertIn("authorized", result["recommended_patch"].lower())

    def test_binary_protocol_signal_is_classified(self):
        stderr = """
zlib.error: Error -3 while decompressing data: incorrect header check
payload looks like binary protobuf/msgpack response, not JSON
"""

        result = classify_scraper_error(stderr)

        self.assertEqual(result["error_type"], "binary_protocol_detected")
        self.assertGreaterEqual(result["confidence"], 0.85)

    def test_slider_400_response_is_classified_as_challenge(self):
        stderr = """
HTTP 400 Bad Request
slider verification failed; expected track payload before data response
"""

        result = classify_scraper_error(stderr)

        self.assertEqual(result["error_type"], "slider_captcha_required")
        self.assertGreaterEqual(result["confidence"], 0.85)

    def test_captcha_html_requires_form_context(self):
        text_only = classify_scraper_error("extraction returned empty", html="<div>captcha status label only</div>")
        form_case = classify_scraper_error(
            "extraction returned empty",
            html="<form id='verify'><input name='captcha'><button>submit</button></form>",
        )

        self.assertNotEqual(text_only["error_type"], "slider_captcha_required")
        self.assertEqual(form_case["error_type"], "slider_captcha_required")

    def test_timestamp_salt_signature_failure_prefers_md5_over_hmac(self):
        stderr = """
signature verification failed
client script evidence: md5(timestamp + static salt)
not an HMAC request signature
"""

        result = classify_scraper_error(stderr)

        self.assertEqual(result["error_type"], "md5_signature_failed")
        self.assertGreaterEqual(result["confidence"], 0.85)


if __name__ == "__main__":
    unittest.main()
