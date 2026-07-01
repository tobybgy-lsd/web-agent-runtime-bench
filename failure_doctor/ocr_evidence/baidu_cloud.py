from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .safety import safety_decision


def run_baidu_cloud_provider(
    provider: str,
    input_path: Path,
    *,
    allow_cloud: bool,
    input_findings: list[str],
    ocr_findings: list[str],
) -> dict[str, Any]:
    safety = safety_decision(
        provider=provider,
        input_findings=input_findings,
        ocr_findings=ocr_findings,
        allow_cloud=allow_cloud,
    )
    if safety["shareability_decision"] == "blocked":
        return _blocked(provider, safety)
    if not os.environ.get("BAIDU_OCR_API_KEY") or not os.environ.get("BAIDU_OCR_SECRET"):
        result = _blocked(provider, safety)
        result["warnings"] = ["provider_unavailable", "baidu_credentials_not_configured"]
        return result
    result = _blocked(provider, safety)
    result["warnings"] = ["provider_unavailable", "cloud_call_not_implemented_in_public_package"]
    return result


def _blocked(provider: str, safety: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": provider,
        "text_blocks": [],
        "tables": [],
        "forms": [],
        "layout": [],
        "warnings": ["cloud_ocr_not_executed"],
        "cloud_blocked": True,
        "safety_override": safety,
        "confidence_summary": {"overall": 0.0, "text": 0.0, "table": 0.0, "form": 0.0},
    }
