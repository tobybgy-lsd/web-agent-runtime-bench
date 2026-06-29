from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DIR = ROOT / "validation"


def write_validation(filename: str, payload: dict[str, Any]) -> dict[str, Any]:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    path = VALIDATION_DIR / filename
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return payload


def pass_status(*conditions: bool) -> str:
    return "pass" if all(conditions) else "fail"


def base_payload(track: str, total_cases: int) -> dict[str, Any]:
    return {
        "schema_version": f"{track}/v1",
        "track": track,
        "fixture_scope": "local_synthetic_public_safe",
        "total_cases": total_cases,
        "real_platform_access_count": 0,
        "private_solution_leak_count": 0,
        "forbidden_output_count": 0,
    }
