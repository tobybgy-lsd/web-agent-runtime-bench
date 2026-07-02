from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .device_farm import MOCK_DEVICE
from .ops_audit import append_audit, write_json


def discover_devices(farm: Path, out: Path, include_mock: bool = True) -> dict[str, Any]:
    devices_path = farm / "devices.json"
    devices = []
    if devices_path.exists():
        devices = json.loads(devices_path.read_text(encoding="utf-8")).get("devices", [])
    if include_mock and not devices:
        devices = [MOCK_DEVICE.copy()]
    payload = {
        "schema_version": "android_device_inventory/v1",
        "devices": devices,
        "local_only": True,
        "no_upload": True,
        "no_telemetry": True,
    }
    write_json(devices_path, payload)
    report = write_json(out / "device_inventory.json", payload)
    append_audit(farm, "farm_discover", {"device_count": len(devices)})
    return report

