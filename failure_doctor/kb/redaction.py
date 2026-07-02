from __future__ import annotations

import re
from typing import Any


_REDACTIONS = (
    (re.compile(r"(?i)(authorization:\s*bearer\s+)[A-Za-z0-9._\-]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(cookie:\s*)[^\n\r]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(api[_ -]?key\s*[:=]\s*)[^\s,\n\r]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(token\s*[:=]\s*)[^\s,\n\r]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(password\s*[:=]\s*)[^\s,\n\r]+"), r"\1[REDACTED]"),
    (re.compile(r"\b\d{11}\b"), "[REDACTED_PHONE]"),
    (re.compile(r"\b\d{15,19}\b"), "[REDACTED_NUMBER]"),
)


def redact_text(text: str, *, limit: int = 2000) -> str:
    result = text[:limit]
    for pattern, repl in _REDACTIONS:
        result = pattern.sub(repl, result)
    return result


def stable_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)) or value is None:
        return str(value)
    if isinstance(value, dict):
        return " ".join(f"{k} {stable_text(v)}" for k, v in sorted(value.items()))
    if isinstance(value, list):
        return " ".join(stable_text(item) for item in value)
    return str(value)
