from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json


def start_session(device_id: str, port: int, out: Path) -> dict[str, Any]:
    payload = {
        "schema_version": "android_appium_session/v1",
        "device_id": device_id,
        "appium_port": port,
        "session_status": "planned",
        "localhost_only": True,
        "real_server_started": False,
    }
    return write_json(out / "session_report.json", payload)


def stop_session(session: Path) -> dict[str, Any]:
    payload = {"schema_version": "android_appium_session/v1", "session_status": "stopped", "session": str(session)}
    out = session if session.suffix == ".json" else session / "session_stopped.json"
    return write_json(out, payload)

