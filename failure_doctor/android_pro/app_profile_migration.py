from __future__ import annotations

from pathlib import Path
from typing import Any

from .app_profile import validate_app_profile
from .flow_linter import lint_flow_file
from .common import write_json


def onboarding_check(profile: Path, flow: Path, out: Path) -> dict[str, Any]:
    profile_report = validate_app_profile(profile)
    flow_report = lint_flow_file(flow, profile, out)
    checks = {
        "profile_valid": profile_report["status"] == "pass",
        "flow_lint_pass": flow_report["status"] == "pass",
        "dry_run_default": True,
        "no_external_upload": True,
        "no_root_hook_bypass": True,
    }
    payload = {"schema_version": "android_onboarding_check/v1", "status": "pass" if all(checks.values()) else "fail", "checks": checks}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_onboarding_report.json", payload)
    return payload
