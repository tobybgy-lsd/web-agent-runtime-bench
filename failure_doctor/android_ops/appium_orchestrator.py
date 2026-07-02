from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ops_audit import write_json
from .port_allocator import allocate_ports


def plan_appium_sessions(farm: Path, out: Path) -> dict[str, Any]:
    devices_path = farm / "devices.json"
    devices = []
    if devices_path.exists():
        devices = json.loads(devices_path.read_text(encoding="utf-8")).get("devices", [])
    sessions = []
    for idx, device in enumerate(devices):
        ports = allocate_ports(idx)
        sessions.append(
            {
                "device_id": device["device_id"],
                **ports,
                "session_status": "planned",
                "log_path": f"sessions/{device['device_id']}/appium.log",
                "localhost_only": True,
            }
        )
    payload = {
        "schema_version": "android_appium_orchestration/v1",
        "sessions": sessions,
        "status": "pass",
        "does_not_start_real_server": True,
        "external_api_call_count": 0,
    }
    return write_json(out / "appium_orchestration_plan.json", payload)

