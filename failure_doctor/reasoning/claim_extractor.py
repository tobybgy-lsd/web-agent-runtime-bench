from __future__ import annotations

from typing import Any


def extract_claims(report: dict[str, Any]) -> list[dict[str, Any]]:
    return list(report.get("claims", []))
