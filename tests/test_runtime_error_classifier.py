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


if __name__ == "__main__":
    unittest.main()
