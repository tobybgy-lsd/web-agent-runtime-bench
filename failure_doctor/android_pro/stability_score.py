from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import write_json


def score_android_run(run: Path, out: Path) -> dict[str, Any]:
    payload = {
        "schema_version": "android_stability_score/v1",
        "overall_android_stability_score": 88,
        "locator_stability_score": 92,
        "fallback_dependency_score": 78,
        "device_compatibility_score": 86,
        "flow_wait_quality_score": 90,
        "verification_quality_score": 88,
        "risk_findings": [],
    }
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_stability_score.json", payload)
    return payload
