from __future__ import annotations

from typing import Any


def evidence_ids(bundle: dict[str, Any]) -> set[str]:
    return {item["evidence_id"] for item in bundle.get("evidence_items", [])}
