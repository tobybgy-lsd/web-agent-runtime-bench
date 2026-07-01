from __future__ import annotations

from typing import Any


def document_structure_from_ocr(ocr: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "document_structure/v1",
        "pages": sorted({block.get("source_page", 1) for block in ocr.get("text_blocks", [])}) or [1],
        "headings": [b for b in ocr.get("text_blocks", []) if float(b.get("confidence", 0)) >= 0.9 and len(b.get("text", "")) < 80],
        "paragraphs": ocr.get("text_blocks", []),
        "tables": ocr.get("tables", []),
        "forms": ocr.get("forms", []),
        "figures": {"unsupported": True, "reason": "provider_does_not_return_figure_structure"},
        "charts": {"unsupported": True, "reason": "provider_does_not_return_chart_structure"},
        "formulas": {"unsupported": True, "reason": "provider_does_not_return_formula_structure"},
        "reading_order": [b.get("id") for b in sorted(ocr.get("text_blocks", []), key=lambda b: b.get("reading_order", 0))],
        "layout_blocks": ocr.get("layout", []),
    }
