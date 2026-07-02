from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json


def android_ops_dashboard_summary(farm: Path | None = None) -> dict[str, Any]:
    return {
        "schema_version": "android_ops_dashboard/v1",
        "status": "pass",
        "title": "Android Ops Center",
        "sections": [
            "Device Farm",
            "Device Health",
            "Appium Sessions",
            "Device Lease",
            "Recovery",
            "Business Templates",
            "Data Binding",
            "Scheduler",
            "Task Queue",
            "Replay",
            "Flaky Detector",
            "Compatibility Report",
            "Mutation Guard",
            "Ops Metrics",
            "Runbook",
        ],
        "raw_screenshot_default_hidden": True,
        "business_mutation_default_blocked": True,
        "final_submit_default_blocked": True,
        "farm": str(farm) if farm else None,
    }


def write_dashboard_summary(out: Path, farm: Path | None = None) -> dict[str, Any]:
    return write_json(out / "android_ops_dashboard.json", android_ops_dashboard_summary(farm))

