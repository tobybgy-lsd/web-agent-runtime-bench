from __future__ import annotations

from .extractor import extract_ocr_evidence
from .consistency import compare_ocr_dom, compare_ocr_vlm
from .validation import validate_ocr_report

__all__ = [
    "compare_ocr_dom",
    "compare_ocr_vlm",
    "extract_ocr_evidence",
    "validate_ocr_report",
]
