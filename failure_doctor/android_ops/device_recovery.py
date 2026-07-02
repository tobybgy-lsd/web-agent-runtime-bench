from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json


ALLOWED_STRATEGIES = {"soft-reset", "app-restart", "session-clean", "mock-recovery"}


def recover_device(device_id: str, strategy: str, out: Path) -> dict[str, Any]:
    status = "pass" if strategy in ALLOWED_STRATEGIES else "blocked"
    payload = {
        "schema_version": "android_device_recovery/v1",
        "device_id": device_id,
        "strategy": strategy,
        "status": status,
        "steps": _steps(strategy) if status == "pass" else [],
        "blocked_reasons": [] if status == "pass" else ["unsupported recovery strategy"],
        "local_only": True,
        "does_not_factory_reset": True,
        "does_not_require_root": True,
        "does_not_modify_apk": True,
    }
    return write_json(out / "device_recovery_report.json", payload)


def _steps(strategy: str) -> list[str]:
    mapping = {
        "soft-reset": ["home", "close_keyboard", "clear_appium_session", "bring_target_app_foreground"],
        "app-restart": ["force_stop_target_package", "start_target_activity"],
        "session-clean": ["close_appium_session", "create_new_session_plan"],
        "mock-recovery": ["record_mock_recovery"],
    }
    return mapping.get(strategy, [])

