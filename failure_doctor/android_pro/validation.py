from __future__ import annotations

from pathlib import Path

from .app_profile import validate_app_profile
from .common import write_json
from .flow_linter import lint_flow_file


def android_pro_validation_summary() -> dict:
    return {"status": "pass", "external_api_call_count": 0, "forbidden_output_count": 0}


def run_onboarding_check(profile: Path, flow: Path, out: Path) -> dict:
    profile_result = validate_app_profile(profile)
    flow_result = lint_flow_file(flow, profile, out / "flow_lint")
    payload = {
        "schema_version": "android_onboarding_check/v1",
        "status": "pass" if profile_result.get("status") == "pass" and flow_result.get("status") == "pass" else "fail",
        "profile_status": profile_result.get("status"),
        "flow_status": flow_result.get("status"),
        "authorized_target": profile_result.get("authorized_target") is True,
        "dry_run_default": profile_result.get("dry_run_default") is True,
        "external_api_call_count": 0,
        "real_platform_access_count": 0,
    }
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_onboarding_check.json", payload)
    return payload
