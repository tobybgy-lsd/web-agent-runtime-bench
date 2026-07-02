from __future__ import annotations

from typing import Any


def ci_summary(validation_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "android_ci_status": validation_payload.get("status", "unknown"),
        "android_cases": validation_payload.get("total_cases", 0),
        "external_api_call_count": validation_payload.get("external_api_call_count", 0),
    }
