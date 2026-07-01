from __future__ import annotations

from pathlib import Path
from typing import Any


def run_paddleocr_vl_local(input_path: Path, *, model_dir: str | None = None) -> dict[str, Any]:
    if not model_dir or not Path(model_dir).exists():
        return {
            "provider": "paddleocr_vl_local",
            "text_blocks": [],
            "tables": [],
            "forms": [],
            "layout": [],
            "warnings": ["provider_unavailable", "local_model_dir_not_configured"],
            "provider_unavailable": True,
            "confidence_summary": {"overall": 0.0, "text": 0.0, "table": 0.0, "form": 0.0},
        }
    return {
        "provider": "paddleocr_vl_local",
        "text_blocks": [],
        "tables": [],
        "forms": [],
        "layout": [],
        "warnings": ["provider_unavailable", "local_paddleocr_vl_runtime_not_configured"],
        "provider_unavailable": True,
        "confidence_summary": {"overall": 0.0, "text": 0.0, "table": 0.0, "form": 0.0},
    }
