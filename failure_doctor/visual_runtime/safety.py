from __future__ import annotations

from typing import Any

from .models import VisualRun


SENSITIVE_MARKERS = (
    "password",
    "token",
    "cookie",
    "authorization",
    "secret",
    "customer",
    "private data",
)


def evaluate_visual_safety(run: VisualRun) -> dict[str, Any]:
    text_parts: list[str] = []
    for collection in (run.ocr, run.vlm_responses, run.observations):
        for item in collection:
            text_parts.append(str(item.get("text") or item.get("summary") or item.get("content") or ""))
    text = "\n".join(text_parts).lower()
    markers = [marker for marker in SENSITIVE_MARKERS if marker in text]
    decision = "blocked" if markers else "safe_to_share"
    return {
        "schema_version": "visual_runtime_safety/v1",
        "shareability": decision,
        "markers": markers,
        "sensitive_screenshot_detected": bool(markers),
        "external_vlm_call_count": 0,
        "screenshot_upload_count": 0,
        "real_platform_access_count": 0,
        "forbidden_output_count": 0,
    }
