from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest import TestCase

from failure_doctor.ocr_evidence.extractor import extract_ocr_evidence


class OcrProviderPolicyTests(TestCase):
    def test_baidu_cloud_provider_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.mkdir(exist_ok=True)
            result = extract_ocr_evidence(root, root / "out", provider="baidu_cloud_ocr")
            self.assertEqual(result["exit_code"], 2)
            self.assertEqual(result["ocr"]["safety"]["shareability_decision"], "blocked")
            self.assertFalse(result["ocr"]["safety"]["cloud_upload_used"])

    def test_sensitive_data_blocks_cloud_provider_even_when_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "input"
            inp.mkdir()
            (inp / "mock_ocr_result.json").write_text(
                json.dumps({"text_blocks": [{"text": "Authorization: Bearer secret-token-123"}]}),
                encoding="utf-8",
            )
            result = extract_ocr_evidence(inp, root / "out", provider="baidu_cloud_doc_parser", allow_cloud_ocr=True)
            self.assertEqual(result["exit_code"], 2)
            self.assertEqual(result["ocr"]["safety"]["shareability_decision"], "blocked")
            self.assertFalse(result["ocr"]["safety"]["cloud_upload_used"])

    def test_paddleocr_missing_dependency_degrades_to_provider_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = extract_ocr_evidence(root, root / "out", provider="paddleocr_vl_local")
            self.assertIn("provider_unavailable", result["ocr"]["warnings"])
            self.assertEqual(result["exit_code"], 0)
