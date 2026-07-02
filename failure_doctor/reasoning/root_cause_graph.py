from __future__ import annotations

from typing import Any


def get_root_cause_graph(report: dict[str, Any]) -> dict[str, Any]:
    return dict(report.get("root_cause_graph", {}))
