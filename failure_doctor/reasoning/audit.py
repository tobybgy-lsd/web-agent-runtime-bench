from __future__ import annotations

from typing import Any


def audit_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": report.get("provider"),
        "reasoning_status": report.get("reasoning_status"),
        "fallback_to_rules": report.get("fallback_to_rules"),
    }
