from __future__ import annotations

from typing import Any


def redact_recorded_step(step: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(step)
    if "text" in redacted:
        redacted["text"] = "[REDACTED_TEXT]"
    return redacted
