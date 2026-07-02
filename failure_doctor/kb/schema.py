from __future__ import annotations

from typing import Any


def validate_case(case: dict[str, Any]) -> list[str]:
    required = ["schema_version", "case_id", "source", "failure_type", "subtype", "evidence_fingerprint", "safety"]
    return [field for field in required if field not in case]
