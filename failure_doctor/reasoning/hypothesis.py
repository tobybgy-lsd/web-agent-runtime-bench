from __future__ import annotations

from typing import Any


def supported_hypotheses(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in report.get("hypotheses", []) if item.get("status") == "supported"]
