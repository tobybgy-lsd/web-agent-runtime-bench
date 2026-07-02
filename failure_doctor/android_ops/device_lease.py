from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .ops_audit import append_audit, write_json


def lease_device(farm: Path, device_id: str, task_id: str, ttl_minutes: int = 60) -> dict[str, Any]:
    leases_path = farm / "leases.json"
    payload = _load_leases(leases_path)
    active = [l for l in payload["leases"] if l.get("device_id") == device_id and l.get("status") == "active"]
    if active:
        result = {
            "schema_version": "android_device_lease_result/v1",
            "status": "blocked",
            "device_id": device_id,
            "task_id": task_id,
            "blocked_reason": "android_device_leased",
        }
        append_audit(farm, "device_lease_blocked", result)
        return result
    now = datetime.now(timezone.utc)
    lease = {
        "device_id": device_id,
        "task_id": task_id,
        "leased_by": "android_ops_scheduler",
        "leased_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat(),
        "status": "active",
    }
    payload["leases"].append(lease)
    write_json(leases_path, payload)
    append_audit(farm, "device_lease", lease)
    return {"schema_version": "android_device_lease_result/v1", **lease, "lease_status": "active", "status": "pass"}


def release_device(farm: Path, device_id: str, task_id: str) -> dict[str, Any]:
    leases_path = farm / "leases.json"
    payload = _load_leases(leases_path)
    released = False
    for lease in payload["leases"]:
        if (
            lease.get("device_id") == device_id
            and lease.get("task_id") == task_id
            and lease.get("status") == "active"
        ):
            lease["status"] = "released"
            released = True
    write_json(leases_path, payload)
    result = {
        "schema_version": "android_device_lease_result/v1",
        "status": "pass" if released else "not_found",
        "device_id": device_id,
        "task_id": task_id,
    }
    append_audit(farm, "device_release", result)
    return result


def _load_leases(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"schema_version": "android_device_lease/v1", "leases": []}
