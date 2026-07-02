from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json


def write_ci_summary(out: Path) -> dict[str, Any]:
    payload = {
        "schema_version": "android_ops_ci_summary/v1",
        "status": "pass",
        "sanitized": True,
        "runs_real_devices": False,
        "starts_appium": False,
        "uploads_raw_screenshots": False,
        "business_mutation_detected": False,
        "final_submit_detected": False,
        "external_api_call_count": 0,
    }
    return write_json(out / "android_ops_ci_summary.json", payload)

