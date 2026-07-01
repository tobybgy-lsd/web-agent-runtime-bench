from __future__ import annotations

from typing import Any


def table_structure_from_ocr(ocr: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "table_structure/v1",
        "tables": ocr.get("tables", []),
        "table_count": len(ocr.get("tables", [])),
        "warnings": [w for table in ocr.get("tables", []) for w in table.get("warnings", [])],
    }
