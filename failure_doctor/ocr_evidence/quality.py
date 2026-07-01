from __future__ import annotations

import re
from typing import Any


def build_ocr_data_quality_report(ocr: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for table in ocr.get("tables", []):
        warnings = table.get("warnings", [])
        if "possible_column_shift" in warnings or table.get("columns", 0) < 2:
            findings.append({"type": "ocr_table_column_shift", "table_id": table.get("id"), "severity": "medium"})
        seen: set[str] = set()
        for row in table.get("cells", []):
            key = "|".join(str(cell) for cell in row) if isinstance(row, list) else str(row)
            if key in seen:
                findings.append({"type": "duplicate_table_rows", "table_id": table.get("id"), "severity": "low"})
                break
            seen.add(key)
        header = [str(cell).lower() for cell in (table.get("cells", [[]])[0] if table.get("cells") else [])]
        if header and "sku" not in " ".join(header):
            findings.append({"type": "sku_column_missing", "table_id": table.get("id"), "severity": "medium"})
    for form in ocr.get("forms", []):
        for field in form.get("fields", []):
            label = str(field.get("label", "")).lower()
            value = str(field.get("value", ""))
            if "price" in label and value and not re.search(r"\d+(?:\.\d+)?", value):
                findings.append({"type": "price_field_not_numeric", "form_id": form.get("id"), "severity": "medium"})
            if "date" in label and value and not re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", value):
                findings.append({"type": "date_field_malformed", "form_id": form.get("id"), "severity": "medium"})
            if not value:
                findings.append({"type": "required_form_field_missing", "form_id": form.get("id"), "severity": "medium"})
    return {
        "schema_version": "ocr_data_quality/v1",
        "status": "pass" if not findings else "warning",
        "finding_count": len(findings),
        "findings": findings,
    }
