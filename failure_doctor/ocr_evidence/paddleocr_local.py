from __future__ import annotations

from pathlib import Path
from typing import Any


def run_paddleocr_local(input_path: Path) -> dict[str, Any]:
    try:
        __import__("paddleocr")
    except Exception:
        return _provider_unavailable("paddleocr_local", "paddleocr_dependency_missing")
    return _provider_unavailable("paddleocr_local", "local_paddleocr_runtime_not_configured")


def _provider_unavailable(provider: str, reason: str) -> dict[str, Any]:
    return {
        "provider": provider,
        "text_blocks": [],
        "tables": [],
        "forms": [],
        "layout": [],
        "warnings": ["provider_unavailable", reason],
        "provider_unavailable": True,
        "confidence_summary": {"overall": 0.0, "text": 0.0, "table": 0.0, "form": 0.0},
    }
