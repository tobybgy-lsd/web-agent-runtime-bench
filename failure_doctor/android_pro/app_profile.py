from __future__ import annotations

from pathlib import Path
from typing import Any

from . import ANDROID_PRO_VERSION
from .common import has_forbidden_text, load_json, utc_now, write_json, write_md


def create_app_profile(package_name: str, out: Path, main_activity: str = ".MainActivity") -> dict[str, Any]:
    payload = {
        "schema_version": "android_app_profile/v1",
        "tool_version": ANDROID_PRO_VERSION,
        "profile_id": package_name.replace(".", "_"),
        "package_name": package_name,
        "main_activity": main_activity,
        "target_kind": "mock_app",
        "authorized_target": True,
        "environment": "local_mock",
        "default_mode": "dry_run",
        "allow_final_submit_default": False,
        "required_permissions": [],
        "known_pages": [],
        "known_webviews": [],
        "locator_registry_ref": "locator_registry/android_locator_registry.json",
        "flow_refs": [],
        "media_policy": {"no_external_upload": True},
        "submit_policy": {"allow_final_submit_default": False, "requires_approval": True},
        "safety": {
            "no_captcha_bypass": True,
            "no_anti_bot_evasion": True,
            "no_fingerprint_spoofing": True,
            "no_apk_modification": True,
            "no_hook": True,
            "no_root_required": True,
            "no_external_upload": True,
        },
        "created_at": utc_now(),
    }
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_app_profile.json", payload)
    write_md(out / "profile_summary.md", "Android App Profile", [f"- Package: `{package_name}`", "- Mode: dry-run", "- Final submit: blocked by default"])
    return payload


def load_app_profile(profile: Path | None) -> dict[str, Any] | None:
    if profile is None:
        return None
    path = profile / "android_app_profile.json" if profile.is_dir() else profile
    return load_json(path)


def validate_app_profile(profile: Path) -> dict[str, Any]:
    payload = load_app_profile(profile) or {}
    findings: list[dict[str, str]] = []
    if payload.get("schema_version") != "android_app_profile/v1":
        findings.append({"severity": "critical", "code": "schema_version_invalid"})
    if not payload.get("package_name"):
        findings.append({"severity": "critical", "code": "package_name_missing"})
    if payload.get("authorized_target") is not True:
        findings.append({"severity": "critical", "code": "android_profile_unauthorized_target"})
    if payload.get("target_kind") in {None, "", "unknown"}:
        findings.append({"severity": "critical", "code": "target_kind_unknown"})
    if payload.get("allow_final_submit_default") is not False:
        findings.append({"severity": "critical", "code": "final_submit_must_default_false"})
    forbidden = has_forbidden_text(str(payload))
    for term in forbidden:
        findings.append({"severity": "critical", "code": "forbidden_profile_content", "term": term})
    report = {
        "schema_version": "android_profile_validation/v1",
        "tool_version": ANDROID_PRO_VERSION,
        "status": "pass" if not findings else "fail",
        "findings": findings,
    }
    out_dir = profile if profile.is_dir() else profile.parent
    write_json(out_dir / "android_profile_validation.json", report)
    return report
