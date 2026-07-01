from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def import_external_json(input_path: Path) -> dict[str, Any]:
    if input_path.is_file():
        return json.loads(input_path.read_text(encoding="utf-8"))
    for candidate in (input_path / "ocr_evidence.json", input_path / "mock_ocr_result.json"):
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return {
        "provider": "external_json_import",
        "text_blocks": [],
        "tables": [],
        "forms": [],
        "layout": [],
        "warnings": ["external_json_missing"],
        "confidence_summary": {"overall": 0.0, "text": 0.0, "table": 0.0, "form": 0.0},
    }
