from __future__ import annotations

from typing import Any


SAFE_TARGET_KINDS = {"mock_app", "internal_app", "owned_app", "authorized_test_app"}

FORBIDDEN_ACTION_TERMS = {
    "captcha": "captcha_or_challenge_bypass_not_supported",
    "turnstile": "captcha_or_challenge_bypass_not_supported",
    "recaptcha": "captcha_or_challenge_bypass_not_supported",
    "bypass": "bypass_instruction_not_allowed",
    "evasion": "evasion_instruction_not_allowed",
    "fingerprint": "fingerprint_spoofing_not_allowed",
    "signature cracking": "dynamic_signature_cracking_not_allowed",
    "dynamic signature": "dynamic_signature_cracking_not_allowed",
    "frida": "instrumentation_not_allowed",
    "xposed": "instrumentation_not_allowed",
    "magisk": "root_or_system_modification_not_allowed",
    "root": "root_or_system_modification_not_allowed",
    "apk patch": "apk_modification_not_allowed",
    "apk modify": "apk_modification_not_allowed",
    "hook": "runtime_hooking_not_allowed",
    "contacts": "private_device_data_not_allowed",
    "sms": "private_device_data_not_allowed",
    "browser profile": "browser_profile_access_not_allowed",
    "device pool": "device_pool_not_allowed",
    "account pool": "account_pool_not_allowed",
}


def _flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{k} {_flatten(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(_flatten(v) for v in value)
    return str(value)


def evaluate_flow_safety(flow: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic safety decision for an Android flow.

    The adapter is designed for owned, internal, mock, or otherwise authorized
    APK UI automation. It blocks high-risk instructions by default and requires
    explicit human approval for final-submit actions.
    """

    blocked: list[str] = []
    warnings: list[str] = []
    if flow.get("authorized_target") is not True:
        blocked.append("authorized_target_required")
    if str(flow.get("target_kind", "")).strip() not in SAFE_TARGET_KINDS:
        blocked.append("authorized_target_kind_required")
    if flow.get("requires_root") is True:
        blocked.append("root_or_system_modification_not_allowed")
    if flow.get("uses_external_ocr") is True:
        blocked.append("external_ocr_upload_not_allowed_by_default")
    if flow.get("uploads_screenshots") is True:
        blocked.append("screenshot_upload_not_allowed")
    if flow.get("access_private_app_dir") is True:
        blocked.append("private_app_directory_access_not_allowed")
    if flow.get("allow_final_submit") is True and not flow.get("approval_id"):
        blocked.append("final_submit_approval_id_required")

    steps = flow.get("steps", [])
    if not isinstance(steps, list):
        blocked.append("steps_must_be_list")
        steps = []
    for step in steps:
        if not isinstance(step, dict):
            blocked.append("step_must_be_object")
            continue
        if step.get("final_submit") is True and not flow.get("allow_final_submit"):
            blocked.append("final_submit_requires_explicit_approval")
        locator = step.get("locator") or {}
        if isinstance(locator, dict) and locator.get("coordinate") and not locator.get("fallback_only"):
            blocked.append("absolute_coordinate_primary_locator_blocked")
        if step.get("action") in {"submit", "post", "publish"} and not flow.get("allow_final_submit"):
            blocked.append("final_submit_requires_explicit_approval")

    haystack = _flatten(flow).lower()
    for term, reason in FORBIDDEN_ACTION_TERMS.items():
        if term in haystack:
            blocked.append(reason)

    if not steps:
        warnings.append("empty_flow")

    unique_blocked = sorted(set(blocked))
    return {
        "schema_version": "android_safety_report/v1",
        "status": "blocked" if unique_blocked else "pass",
        "safe_next_action": not unique_blocked,
        "blocked_reasons": unique_blocked,
        "warnings": sorted(set(warnings)),
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "real_platform_access_count": 0,
        "browser_profile_access_count": 0,
        "credential_store_access_count": 0,
        "active_probe_count": 0,
    }
