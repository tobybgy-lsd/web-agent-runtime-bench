from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import is_final_action_text, write_json


def evaluate_publish_guard(action: dict[str, Any], out: Path | None = None) -> dict[str, Any]:
    text = str(action.get("text") or action.get("value") or action.get("action") or "")
    allow = bool(action.get("allow_final_submit"))
    blocked = is_final_action_text(text) and not allow
    report = {
        "schema_version": "android_publish_guard/v1",
        "decision": "blocked" if blocked else "allowed",
        "reason": "final submit is blocked by default" if blocked else "no final submit risk detected",
        "requires_approval": blocked,
    }
    if out:
        write_json(out / "publish_guard_report.json", report)
    return report
