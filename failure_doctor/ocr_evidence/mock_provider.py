from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_mock_ocr_result(input_path: Path) -> dict[str, Any]:
    candidates: list[Path] = []
    if input_path.is_dir():
        candidates.extend(
            [
                input_path / "mock_ocr_result.json",
                input_path.parent / "mock_ocr_result.json",
                input_path / "input" / "mock_ocr_result.json",
            ]
        )
    else:
        candidates.extend([input_path.with_name("mock_ocr_result.json"), input_path.parent / "mock_ocr_result.json"])
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return {
        "provider": "mock_ocr",
        "text_blocks": [],
        "tables": [],
        "forms": [],
        "layout": [],
        "warnings": ["mock_ocr_result_missing"],
        "confidence_summary": {"overall": 0.0, "text": 0.0, "table": 0.0, "form": 0.0},
    }
