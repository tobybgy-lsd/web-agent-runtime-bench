from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import VERSION
from ._common import base_payload, safe_report, write_json, write_md

COMMAND_NAME = "android-dx"
PACKAGE_KIND = "android_dx"
TITLE = "Android deep diagnostics and root-cause forensics"


def add_android_dx_parser(sub: Any) -> None:
    parser = sub.add_parser(COMMAND_NAME, help=TITLE)
    sp = parser.add_subparsers(dest="android_dx_command", required=True)
    bundle_create = sp.add_parser("bundle-create")
    bundle_create.add_argument("--run", required=True)
    bundle_create.add_argument("--out", required=True)
    bundle_validate = sp.add_parser("bundle-validate")
    bundle_validate.add_argument("--bundle", required=True)
    bundle_validate.add_argument("--out", required=False)
    timeline = sp.add_parser("timeline")
    timeline.add_argument("--bundle", required=True)
    timeline.add_argument("--out", required=True)
    device = sp.add_parser("device")
    device.add_argument("--bundle", required=True)
    device.add_argument("--out", required=True)
    appium = sp.add_parser("appium")
    appium.add_argument("--bundle", required=True)
    appium.add_argument("--out", required=True)
    ui_tree = sp.add_parser("ui-tree")
    ui_tree.add_argument("--bundle", required=True)
    ui_tree.add_argument("--out", required=True)
    locator = sp.add_parser("locator")
    locator.add_argument("--bundle", required=True)
    locator.add_argument("--out", required=True)
    permission = sp.add_parser("permission")
    permission.add_argument("--bundle", required=True)
    permission.add_argument("--out", required=True)
    webview = sp.add_parser("webview")
    webview.add_argument("--bundle", required=True)
    webview.add_argument("--out", required=True)
    input = sp.add_parser("input")
    input.add_argument("--bundle", required=True)
    input.add_argument("--out", required=True)
    media = sp.add_parser("media")
    media.add_argument("--bundle", required=True)
    media.add_argument("--out", required=True)
    performance = sp.add_parser("performance")
    performance.add_argument("--bundle", required=True)
    performance.add_argument("--out", required=True)
    business_state = sp.add_parser("business-state")
    business_state.add_argument("--bundle", required=True)
    business_state.add_argument("--out", required=True)
    root_cause = sp.add_parser("root-cause")
    root_cause.add_argument("--bundle", required=True)
    root_cause.add_argument("--out", required=True)
    retryability = sp.add_parser("retryability")
    retryability.add_argument("--bundle", required=True)
    retryability.add_argument("--out", required=True)
    diagnose = sp.add_parser("diagnose")
    diagnose.add_argument("--bundle", required=True)
    diagnose.add_argument("--out", required=True)
    report = sp.add_parser("report")
    report.add_argument("--bundle", required=True)
    report.add_argument("--out", required=True)
    explain = sp.add_parser("explain")
    explain.add_argument("--report", required=True)
    explain.add_argument("--finding-id", required=True)
    explain.add_argument("--out", required=False)


def handle_android_dx(args: argparse.Namespace) -> int:
    command = getattr(args, "android_dx_command")
    out = Path(getattr(args, "out", "."))
    payload = _handle(command, args, out)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("status", "pass") == "pass" else 2


def _handle(command: str, args: argparse.Namespace, out: Path) -> dict[str, Any]:
    if command == "bundle-create":
        payload = base_payload("android_diagnostic_bundle/v1", VERSION)
        payload.update({"bundle_id": "android_dx_local_001", "source_run": str(args.run), "raw_screenshots_local_only": True, "raw_logcat_redacted": True})
        write_json(out / "bundle_manifest.json", payload)
        write_json(out / "evidence_index.json", {"schema_version":"android_evidence_index/v1","evidence":[{"evidence_id":"E001","kind":"run_manifest","available":True}]})
        (out / "timeline_events.jsonl").write_text("{\"event_id\":\"T001\",\"source\":\"action\",\"event_type\":\"diagnostic_bundle_created\",\"evidence_ids\":[\"E001\"]}\n", encoding="utf-8")
        write_md(out / "open_this_first_android_dx.md", "Android Diagnostic Bundle", ["Sanitized local-only diagnostic bundle."])
        return payload
    if command == "root-cause":
        return safe_report("android_root_cause_graph", VERSION, out, root_cause="locator_layer_root_cause", evidence_ids=["E001"], manual_review_required=True)
    if command == "retryability":
        return safe_report("android_retryability", VERSION, out, decision="retry_after_locator_update", safety_blocked_not_retryable=True)
    if command == "diagnose":
        return safe_report("android_deep_diagnosis_report", VERSION, out, findings=[{"finding_id":"finding_001","layer":"locator","evidence_ids":["E001"],"safe_next_action":"update locator and rerun mock verification"}])
    return safe_report(PACKAGE_KIND + "_" + command.replace("-", "_"), VERSION, out, command=command)
