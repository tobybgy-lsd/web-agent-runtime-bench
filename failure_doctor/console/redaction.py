from __future__ import annotations

import json
import re
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization:\s*bearer\s+)[^\s\"']+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s\"']+"),
    re.compile(r"(?i)(password\s*[:=]\s*)[^\s\"']+"),
    re.compile(r"(?i)(token\s*[:=]\s*)[^\s\"']+"),
    re.compile(r"(?i)(cookie\s*[:=]\s*)[^\n\r]+"),
]


def redact_text(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}[REDACTED]", redacted)
    return redacted


def redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): redact_value(item) for key, item in value.items()}
    return value


def dumps_json(payload: Any) -> str:
    return json.dumps(redact_value(payload), ensure_ascii=False, indent=2)
