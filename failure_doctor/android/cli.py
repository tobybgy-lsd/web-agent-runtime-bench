from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .devices import doctor_report, list_devices
from .diagnosis import write_android_diagnosis
from .flow import validate_flow_file
from .flow_runner import run_flow_file
from .normalizer import normalize_android_input
from .replay import replay_run_report
from .report import write_android_report
from .ui_tree import write_ui_tree_outputs


def add_android_parser(sub: Any) -> None:
    android = sub.add_parser("android", help="Local-only Android APK UI automation evidence adapter")
    android_sub = android.add_subparsers(dest="android_command", required=True)

    doctor = android_sub.add_parser("doctor", help="Check local Android tooling availability")
    doctor.add_argument("--out", default=None)

    devices = android_sub.add_parser("devices", help="List local adb devices when adb is available")
    devices.add_argument("--out", default=None)

    normalize = android_sub.add_parser("normalize", help="Normalize Android APK UI evidence into a failure pack")
    normalize.add_argument("input")
    normalize.add_argument("--out", required=True)

    diagnose = android_sub.add_parser("diagnose", help="Diagnose a normalized Android APK UI failure pack")
    diagnose.add_argument("input")
    diagnose.add_argument("--out", required=True)

    validate = android_sub.add_parser("validate-flow", help="Validate an authorized Android UI flow")
    validate.add_argument("flow")
    validate.add_argument("--out", required=True)

    run = android_sub.add_parser("run-flow", help="Run an Android UI flow in safe dry-run mode by default")
    run.add_argument("flow")
    run.add_argument("--out", required=True)
    run.add_argument("--farm", default=None, help="Optional Android Ops farm manifest for planning context")
    run.add_argument("--dry-run", action="store_true", default=True)

    replay = android_sub.add_parser("replay", help="Replay an Android run report without touching a device")
    replay.add_argument("report")
    replay.add_argument("--out", required=True)

    dump = android_sub.add_parser("dump-ui", help="Normalize a uiautomator XML dump")
    dump.add_argument("xml")
    dump.add_argument("--out", required=True)

    screenshot = android_sub.add_parser("screenshot", help="Write a screenshot evidence placeholder or normalize provided file")
    screenshot.add_argument("--input", default=None)
    screenshot.add_argument("--out", required=True)

    logcat = android_sub.add_parser("logcat-summary", help="Summarize a saved logcat file")
    logcat.add_argument("logcat")
    logcat.add_argument("--out", required=True)

    inspect = android_sub.add_parser("inspect", help="Inspect a local Android evidence folder")
    inspect.add_argument("input")
    inspect.add_argument("--out", required=True)

    export = android_sub.add_parser("export-report", help="Export a compact Android report JSON/Markdown pair")
    export.add_argument("input")
    export.add_argument("--out", required=True)


def handle_android(args: Any) -> int:
    command = args.android_command
    if command == "doctor":
        payload = doctor_report()
        _maybe_write(payload, args.out, "android_doctor")
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    if command == "devices":
        payload = list_devices()
        _maybe_write(payload, args.out, "android_devices")
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    if command == "normalize":
        payload = normalize_android_input(Path(args.input), Path(args.out))
        print(f"Android APK adapter normalized: {payload.get('candidate_subtype')}")
        return 0
    if command == "diagnose":
        payload = write_android_diagnosis(Path(args.input), Path(args.out))
        print(f"Android APK diagnosis: {payload.get('subtype')}")
        return 0
    if command == "validate-flow":
        payload = validate_flow_file(Path(args.flow))
        _maybe_write(payload, args.out, "android_flow_validation")
        print(f"Android flow validation: {payload.get('status')}")
        return 0 if payload.get("status") == "pass" else 2
    if command == "run-flow":
        payload = run_flow_file(Path(args.flow), Path(args.out), dry_run=True)
        print(f"Android flow run: {payload.get('status')}")
        return 0 if payload.get("status") == "pass" else 2
    if command == "replay":
        payload = replay_run_report(Path(args.report), Path(args.out))
        print(f"Android replay: {payload.get('status')}")
        return 0 if payload.get("status") == "pass" else 2
    if command == "dump-ui":
        payload = write_ui_tree_outputs(Path(args.xml), Path(args.out))
        print(f"Android UI nodes: {payload.get('node_count')}")
        return 0
    if command == "screenshot":
        payload = {
            "schema_version": "android_screenshot/v1",
            "status": "pass",
            "input": args.input,
            "note": "No device screenshot is captured unless a user supplies authorized evidence.",
        }
        _maybe_write(payload, args.out, "android_screenshot")
        print("Android screenshot evidence recorded")
        return 0
    if command == "logcat-summary":
        text = Path(args.logcat).read_text(encoding="utf-8", errors="ignore")
        payload = {
            "schema_version": "android_logcat_summary/v1",
            "status": "pass",
            "line_count": len(text.splitlines()),
            "contains_crash": "fatal exception" in text.lower(),
            "contains_permission": "permission" in text.lower(),
        }
        _maybe_write(payload, args.out, "android_logcat_summary")
        print("Android logcat summarized")
        return 0
    if command in {"inspect", "export-report"}:
        payload = normalize_android_input(Path(args.input), Path(args.out))
        write_android_report(payload, Path(args.out), "android_export_report")
        print("Android report exported")
        return 0
    return 1


def _maybe_write(payload: dict[str, Any], out: str | None, name: str) -> None:
    if not out:
        return
    output = Path(out)
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{name}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
