from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RULES: list[tuple[str, tuple[str, ...], str, float]] = [
    ("android_permission_dialog_blocked", ("permission denial", "permission dialog", "allow permission"), "anti_bot_risk", 0.91),
    ("android_media_permission_denied", ("read_media", "media permission", "photos permission"), "anti_bot_risk", 0.9),
    ("android_app_crashed", ("fatal exception", "app crash", "force close"), "automation_engineering", 0.9),
    ("android_app_not_installed", ("not installed", "unknown package", "package does not exist"), "environment", 0.89),
    ("android_app_launch_failed", ("activity not started", "unable to start activity", "launch failed"), "automation_engineering", 0.88),
    ("android_device_not_found", ("no devices/emulators found", "device not found", "adb: no devices"), "environment", 0.9),
    ("android_appium_unavailable", ("appium not found", "could not connect to appium", "webdriveragent"), "environment", 0.88),
    ("android_uiautomator_dump_failed", ("uiautomator dump failed", "xml dump failed"), "automation_engineering", 0.87),
    ("android_locator_not_found", ("no such element", "element not found", "locator not found"), "automation_engineering", 0.86),
    ("android_duplicate_locator_candidates", ("multiple elements", "ambiguous locator", "duplicate candidates"), "automation_engineering", 0.86),
    ("android_resource_id_changed", ("resource-id changed", "id drift", "old id not found"), "website_change", 0.84),
    ("android_text_changed", ("text changed", "label changed"), "website_change", 0.84),
    ("android_content_desc_missing", ("content-desc missing", "accessibility id missing"), "automation_engineering", 0.84),
    ("android_ui_tree_stale", ("stale ui tree", "stale object", "snapshot stale"), "automation_engineering", 0.85),
    ("android_webview_context_mismatch", ("webview context", "native_app context", "context mismatch"), "automation_engineering", 0.88),
    ("android_keyboard_input_failed", ("keyboard input failed", "ime", "soft keyboard"), "automation_engineering", 0.83),
    ("android_toast_error_detected", ("toast", "snackbar", "error toast"), "automation_engineering", 0.82),
    ("android_publish_button_disabled", ("publish button disabled", "submit button disabled", "button disabled"), "automation_engineering", 0.86),
    ("android_final_submit_blocked_by_policy", ("final submit blocked", "final_submit_requires_explicit_approval"), "anti_bot_risk", 0.95),
    ("android_ocr_fallback_low_confidence", ("ocr confidence", "low ocr", "ocr fallback"), "insufficient_evidence", 0.78),
    ("android_image_fallback_low_confidence", ("image match confidence", "low image match"), "insufficient_evidence", 0.78),
    ("android_coordinate_fallback_required", ("coordinate fallback", "tap coordinate"), "automation_engineering", 0.76),
    ("android_flow_unsafe_blocked", ("unsafe flow blocked", "blocked_reasons"), "anti_bot_risk", 0.94),
]


def _read_pack_text(input_dir: Path) -> str:
    parts: list[str] = []
    if input_dir.is_file():
        return input_dir.read_text(encoding="utf-8", errors="ignore")
    for pattern in ("*.txt", "*.log", "*.json", "*.xml", "*.md"):
        for path in sorted(input_dir.rglob(pattern)):
            if path.is_file() and path.stat().st_size <= 2_000_000:
                parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def diagnose_android_pack(input_dir: Path | str) -> dict[str, Any]:
    source = Path(input_dir)
    text = _read_pack_text(source)
    lower = text.lower()
    matched = None
    for subtype, needles, category, confidence in RULES:
        if any(needle in lower for needle in needles):
            matched = (subtype, category, confidence)
            break
    if matched is None:
        matched = ("android_insufficient_evidence", "insufficient_evidence", 0.55)
    subtype, category, confidence = matched
    return {
        "schema_version": "android_diagnosis/v1",
        "technical_category": category,
        "failure_layer": category,
        "subtype": subtype,
        "confidence": confidence,
        "evidence": [{"kind": "android_pack_text", "summary": text[:500]}] if text else [],
        "next_action": _next_action(subtype),
        "safe_next_action": category != "anti_bot_risk" or subtype.startswith("android_final_submit") is False,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "real_platform_access_count": 0,
    }


def _next_action(subtype: str) -> str:
    if subtype == "android_permission_dialog_blocked":
        return "Capture permission dialog evidence, grant only required app permissions in an authorized test profile, then rerun."
    if subtype == "android_final_submit_blocked_by_policy":
        return "Keep the run in dry-run mode unless a human approval id explicitly authorizes final submission."
    if subtype == "android_locator_not_found":
        return "Dump a fresh UI tree and prefer resource-id or accessibility-id locators over coordinates."
    if subtype == "android_webview_context_mismatch":
        return "Record native and WebView contexts and switch only after the expected context is visible."
    return "Collect UI tree, screenshot metadata, logcat summary, and flow definition before changing the script."


def write_android_diagnosis(input_dir: Path | str, out_dir: Path | str) -> dict[str, Any]:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    payload = diagnose_android_pack(input_dir)
    (output / "android_diagnosis.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "diagnosis.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "diagnosis.md").write_text(
        f"# Android APK Diagnosis\n\nSubtype: `{payload['subtype']}`\n\nNext action: {payload['next_action']}\n",
        encoding="utf-8",
    )
    return payload
