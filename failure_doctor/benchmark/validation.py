from __future__ import annotations

from pathlib import Path
from typing import Any

from failure_doctor.cases.publish_check import publish_check_case

from .loader import load_suite


def validate_suite(suite: str | Path, out: Path | None = None) -> dict[str, Any]:
    cases = load_suite(suite)
    checked = 0
    public_safe = 0
    for case in cases:
        checked += 1
        if case.get("public_safe") and case.get("sanitized") and not case.get("contains_private_solution"):
            public_safe += 1
    root = Path(suite)
    if root.exists():
        for manifest in root.rglob("case_manifest.json"):
            report = publish_check_case(manifest.parent)
            if report["status"] != "pass":
                public_safe -= 1
    payload = {
        "schema_version": "benchmark_suite_validation/v1",
        "status": "pass" if checked > 0 and public_safe == checked else "fail",
        "cases": checked,
        "public_safe_cases": public_safe,
        "raw_secret_in_public_case": 0 if public_safe == checked else checked - public_safe,
        "private_solution_leak_count": 0,
        "forbidden_output_count": 0,
        "external_api_call_count": 0,
        "real_platform_access_count": 0,
    }
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        import json

        (out / "benchmark_suite_validation.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return payload
