from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from integrations.cross_framework.common import normalize_framework_failure


class CrossFrameworkCommonTests(unittest.TestCase):
    def test_normalizes_selenium_log_to_failure_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "error.log").write_text(
                "selenium.common.exceptions.NoSuchElementException: Unable to locate element: .submit",
                encoding="utf-8",
            )
            out = root / "pack"

            metadata = normalize_framework_failure(root, "selenium", out)

            self.assertEqual(metadata["schema_version"], "framework_failure_pack/v1")
            self.assertEqual(metadata["framework"], "selenium")
            self.assertEqual(metadata["candidate_technical_category"], "selector_drift")
            self.assertEqual(metadata["subtype"], "selenium_no_such_element")
            self.assertTrue((out / "error.log").exists())
            self.assertTrue((out / "framework_metadata.json").exists())
            self.assertIn("AFD_TECHNICAL_CATEGORY=selector_drift", (out / "error.log").read_text(encoding="utf-8"))

    def test_redacts_secret_like_values_and_marks_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "error.log").write_text(
                "requests.exceptions.ProxyError: proxy failed\nAuthorization: Bearer abc.def.ghi",
                encoding="utf-8",
            )
            out = root / "pack"

            metadata = normalize_framework_failure(root, "requests", out)

            text = (out / "error.log").read_text(encoding="utf-8")
            self.assertNotIn("abc.def.ghi", text)
            self.assertIn("[REDACTED]", text)
            self.assertEqual(metadata["redaction_status"], "redacted")
            self.assertFalse(metadata["safe_to_share"])

    def test_empty_input_degrades_to_insufficient_evidence_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "pack"

            metadata = normalize_framework_failure(root, "auto", out)

            self.assertEqual(metadata["framework"], "auto")
            self.assertEqual(metadata["candidate_failure_layer"], "insufficient_evidence")
            self.assertEqual(metadata["candidate_technical_category"], "insufficient_evidence")
            self.assertIn("insufficient_evidence", (out / "error.log").read_text(encoding="utf-8"))
            parsed = json.loads((out / "framework_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(parsed["schema_version"], "framework_failure_pack/v1")


if __name__ == "__main__":
    unittest.main()
