from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ops_audit import write_json


def check_device_health(device_id: str, out: Path, farm: Path | None = None) -> dict[str, Any]:
    device = _find_device(device_id, farm) if farm else None
    offline = device is not None and device.get("status") == "offline"
    checks = [
        {"name": "adb_availability", "status": "mock_pass"},
        {"name": "device_online", "status": "fail" if offline else "pass"},
        {"name": "uiautomator_dump", "status": "mock_pass"},
        {"name": "screenshot", "status": "mock_pass"},
        {"name": "logcat_summary", "status": "mock_pass"},
        {"name": "appium_reachability", "status": "mock_unavailable", "severity": "warning"},
    ]
    payload = {
        "schema_version": "android_device_health/v1",
        "device_id": device_id,
        "status": "offline" if offline else "healthy",
        "checks": checks,
        "safe_to_run": not offline,
        "warnings": ["Appium not started; orchestration plan only"] if not offline else [],
        "blocked_reasons": ["device offline"] if offline else [],
        "local_only": True,
        "no_upload": True,
    }
    return write_json(out / "device_health_report.json", payload)


def _find_device(device_id: str, farm: Path | None) -> dict[str, Any] | None:
    if not farm:
        return None
    path = farm / "devices.json"
    if not path.exists():
        return None
    for device in json.loads(path.read_text(encoding="utf-8")).get("devices", []):
        if device.get("device_id") == device_id:
            return device
    return None

