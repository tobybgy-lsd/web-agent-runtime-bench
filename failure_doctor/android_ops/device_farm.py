from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import ANDROID_OPS_VERSION
from .ops_audit import append_audit, write_json


MOCK_DEVICE = {
    "device_id": "mock-emulator-5554",
    "name": "Mock Pixel API 34",
    "kind": "mock_device",
    "android_api": 34,
    "screen": "1080x1920",
    "dpi": 420,
    "status": "available",
    "tags": ["mock", "dry_run", "local_only"],
}


def init_farm(out: Path) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    for child in ("health", "sessions", "appium", "reports"):
        (out / child).mkdir(exist_ok=True)
    manifest = {
        "schema_version": "android_device_farm/v1",
        "tool_version": ANDROID_OPS_VERSION,
        "farm_id": "local_android_farm",
        "local_only": True,
        "no_upload": True,
        "no_telemetry": True,
        "device_count": 0,
        "default_mode": "dry_run",
        "business_mutation_default": False,
    }
    devices = {"schema_version": "android_device_inventory/v1", "devices": []}
    leases = {"schema_version": "android_device_lease/v1", "leases": []}
    write_json(out / "farm_manifest.json", manifest)
    write_json(out / "devices.json", devices)
    write_json(out / "leases.json", leases)
    append_audit(out, "farm_init", {"farm_id": manifest["farm_id"]})
    return manifest


def farm_status(farm: Path) -> dict[str, Any]:
    manifest = _read_json(farm / "farm_manifest.json", {})
    devices = _read_json(farm / "devices.json", {"devices": []}).get("devices", [])
    leases = _read_json(farm / "leases.json", {"leases": []}).get("leases", [])
    active = [lease for lease in leases if lease.get("status") == "active"]
    return {
        "schema_version": "android_device_farm_status/v1",
        "tool_version": ANDROID_OPS_VERSION,
        "status": "pass" if manifest else "missing",
        "farm": str(farm),
        "device_count": len(devices),
        "available_devices": sum(1 for d in devices if d.get("status") == "available"),
        "active_leases": len(active),
        "local_only": True,
        "no_upload": True,
        "no_telemetry": True,
    }


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

