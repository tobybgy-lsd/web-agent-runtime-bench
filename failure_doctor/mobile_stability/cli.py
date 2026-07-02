from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import VERSION
from ._common import base_payload, safe_report, write_json, write_md

COMMAND_NAME = "mobile-stability"
PACKAGE_KIND = "mobile_stability"
TITLE = "Mobile automation stable standardization"


def add_mobile_stability_parser(sub: Any) -> None:
    parser = sub.add_parser(COMMAND_NAME, help=TITLE)
    sp = parser.add_subparsers(dest="mobile_stability_command", required=True)
    check_android_cli = sp.add_parser("check-android-cli")
    check_android_cli.add_argument("--out", required=True)
    check_android_schema = sp.add_parser("check-android-schema")
    check_android_schema.add_argument("--out", required=True)
    check_android_plugin_abi = sp.add_parser("check-android-plugin-abi")
    check_android_plugin_abi.add_argument("--out", required=True)
    compatibility = sp.add_parser("compatibility")
    compatibility.add_argument("--from", required=True)
    compatibility.add_argument("--to", required=True)
    compatibility.add_argument("--out", required=True)
    migration_guide = sp.add_parser("migration-guide")
    migration_guide.add_argument("--from", required=True)
    migration_guide.add_argument("--to", required=True)
    migration_guide.add_argument("--out", required=True)
    deprecation_report = sp.add_parser("deprecation-report")
    deprecation_report.add_argument("--out", required=True)


def handle_mobile_stability(args: argparse.Namespace) -> int:
    command = getattr(args, "mobile_stability_command")
    out = Path(getattr(args, "out", "."))
    payload = _handle(command, args, out)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("status", "pass") == "pass" else 2


def _handle(command: str, args: argparse.Namespace, out: Path) -> dict[str, Any]:
    if command == "check-android-cli":
        return safe_report("android_cli_contract", VERSION, out, stable_android_cli_contract=True, command_groups=["android","android-pro","android-ops","android-author","android-pilot","android-dx","android-playbook","android-real-pilot","android-lab","mobile-stability"])
    if command == "check-android-schema":
        return safe_report("android_stable_schema_registry", VERSION, out, stable_android_schema_registry_complete=True)
    if command == "check-android-plugin-abi":
        return safe_report("android_plugin_abi_report", VERSION, out, android_plugin_abi_contract_pass=True)
    if command == "migration-guide":
        return safe_report("android_migration_guide", VERSION, out, migration_guide_generated=True)
    if command == "deprecation-report":
        return safe_report("android_deprecation_report", VERSION, out, deprecation_report_generated=True)
    return safe_report(PACKAGE_KIND + "_" + command.replace("-", "_"), VERSION, out, command=command)
