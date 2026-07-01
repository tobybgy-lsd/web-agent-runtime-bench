from __future__ import annotations

OCR_PROVIDERS = {
    "mock_ocr",
    "paddleocr_local",
    "paddleocr_vl_local",
    "baidu_cloud_ocr",
    "baidu_cloud_doc_parser",
    "external_json_import",
}

CLOUD_PROVIDERS = {"baidu_cloud_ocr", "baidu_cloud_doc_parser"}
LOCAL_PROVIDERS = {"mock_ocr", "paddleocr_local", "paddleocr_vl_local", "external_json_import"}

TOOL_VERSION = "3.5.0"
SCHEMA_VERSION = "ocr_evidence/v1"
