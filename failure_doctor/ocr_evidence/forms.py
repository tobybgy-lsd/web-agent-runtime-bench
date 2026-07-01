from __future__ import annotations

from typing import Any


def form_structure_from_ocr(ocr: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "form_structure/v1",
        "forms": ocr.get("forms", []),
        "form_count": len(ocr.get("forms", [])),
        "field_count": sum(len(form.get("fields", [])) for form in ocr.get("forms", [])),
    }
