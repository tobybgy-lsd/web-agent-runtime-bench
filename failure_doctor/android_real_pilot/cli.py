from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import VERSION
from ._common import base_payload, safe_report, write_json, write_md

COMMAND_NAME = "android-real-pilot"
PACKAGE_KIND = "android_real_pilot"
TITLE = "Real APK private pilot support"


def add_android_real_pilot_parser(sub: Any) -> None:
    parser = sub.add_parser(COMMAND_NAME, help=TITLE)
    sp = parser.add_subparsers(dest="android_real_pilot_command", required=True)
    init = sp.add_parser("init")
    init.add_argument("--out", required=True)
    intake = sp.add_parser("intake")
    intake.add_argument("--workspace", required=True)
    intake.add_argument("--out", required=True)
    import_ui = sp.add_parser("import-ui")
    import_ui.add_argument("--workspace", required=True)
    import_ui.add_argument("--ui-dump", required=True)
    import_ui.add_argument("--out", required=True)
    dry_run_check = sp.add_parser("dry-run-check")
    dry_run_check.add_argument("--workspace", required=True)
    dry_run_check.add_argument("--out", required=True)
    sanitize = sp.add_parser("sanitize")
    sanitize.add_argument("--workspace", required=True)
    sanitize.add_argument("--out", required=True)
    acceptance = sp.add_parser("acceptance")
    acceptance.add_argument("--workspace", required=True)
    acceptance.add_argument("--out", required=True)
    public_summary = sp.add_parser("public-summary")
    public_summary.add_argument("--workspace", required=True)
    public_summary.add_argument("--out", required=True)
    validate = sp.add_parser("validate")
    validate.add_argument("--workspace", required=True)
    validate.add_argument("--out", required=False)


def handle_android_real_pilot(args: argparse.Namespace) -> int:
    command = getattr(args, "android_real_pilot_command")
    out = Path(getattr(args, "out", "."))
    payload = _handle(command, args, out)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("status", "pass") == "pass" else 2


def _handle(command: str, args: argparse.Namespace, out: Path) -> dict[str, Any]:
    if command == "init":
        payload = base_payload("android_real_pilot_workspace/v1", VERSION)
        payload.update({"private_workspace": True, "public_examples_allowed": "mock_only"})
        write_json(out / "real_pilot_workspace.json", payload)
        return payload
    if command == "sanitize":
        return safe_report("android_real_pilot_sanitized", VERSION, out, sanitization_success=True, real_ui_dump_not_public=True)
    if command == "public-summary":
        return safe_report("android_public_pilot_summary", VERSION, out, public_summary_safe=True, sanitized_only=True)
    return safe_report(PACKAGE_KIND + "_" + command.replace("-", "_"), VERSION, out, command=command)
