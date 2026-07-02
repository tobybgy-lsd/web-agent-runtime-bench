from __future__ import annotations

from typing import Any


def build_dry_run_capabilities(package_name: str, activity: str | None = None) -> dict[str, Any]:
    return {
        "platformName": "Android",
        "appium:appPackage": package_name,
        "appium:appActivity": activity,
        "appium:noReset": True,
        "failureDoctorMode": "dry_run_only",
    }
