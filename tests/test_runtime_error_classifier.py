import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "demo" / "phase5_2_runtime"))

from runtime_error_classifier import classify_runtime_error


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


if __name__ == "__main__":
    unittest.main()
