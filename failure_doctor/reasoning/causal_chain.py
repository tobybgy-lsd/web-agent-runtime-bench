from __future__ import annotations

from typing import Any


def get_causal_chain(report: dict[str, Any]) -> dict[str, Any]:
    return dict(report.get("causal_chain", {}))
