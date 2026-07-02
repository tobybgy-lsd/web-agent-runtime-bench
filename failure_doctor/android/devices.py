from __future__ import annotations

import shutil
import subprocess
from typing import Any


def doctor_report() -> dict[str, Any]:
    adb = shutil.which("adb")
    appium = shutil.which("appium")
    return {
        "schema_version": "android_doctor/v1",
        "status": "pass",
        "adb_available": bool(adb),
        "adb_path": adb,
        "appium_available": bool(appium),
        "appium_path": appium,
        "mode": "local_only",
        "notes": ["No device data is read unless the user runs an explicit Android command."],
        "forbidden_output_count": 0,
        "real_platform_access_count": 0,
    }


def list_devices() -> dict[str, Any]:
    adb = shutil.which("adb")
    if not adb:
        return {"schema_version": "android_devices/v1", "status": "unavailable", "devices": [], "reason": "adb_not_found"}
    proc = subprocess.run([adb, "devices", "-l"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    devices = []
    for line in proc.stdout.splitlines()[1:]:
        line = line.strip()
        if line:
            parts = line.split()
            devices.append({"serial": parts[0], "state": parts[1] if len(parts) > 1 else "unknown", "raw": line})
    return {"schema_version": "android_devices/v1", "status": "pass", "devices": devices}
