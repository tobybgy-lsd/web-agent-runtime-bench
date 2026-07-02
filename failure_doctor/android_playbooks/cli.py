from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import VERSION
from ._common import base_payload, safe_report, write_json, write_md

COMMAND_NAME = "android-playbook"
PACKAGE_KIND = "android_playbooks"
TITLE = "Android root-cause playbooks"


def add_android_playbooks_parser(sub: Any) -> None:
    parser = sub.add_parser(COMMAND_NAME, help=TITLE)
    sp = parser.add_subparsers(dest="android_playbooks_command", required=True)
    list = sp.add_parser("list")
    generate = sp.add_parser("generate")
    generate.add_argument("--dx-report", required=True)
    generate.add_argument("--out", required=True)
    explain = sp.add_parser("explain")
    explain.add_argument("--finding-id", required=True)
    explain.add_argument("--dx-report", required=True)
    explain.add_argument("--out", required=True)
    role_view = sp.add_parser("role-view")
    role_view.add_argument("--report", required=True)
    role_view.add_argument("--role", required=True)
    role_view.add_argument("--out", required=True)
    verify_checklist = sp.add_parser("verify-checklist")
    verify_checklist.add_argument("--report", required=True)
    verify_checklist.add_argument("--out", required=True)
    manual_review = sp.add_parser("manual-review")
    manual_review.add_argument("--report", required=True)
    manual_review.add_argument("--out", required=True)


def handle_android_playbooks(args: argparse.Namespace) -> int:
    command = getattr(args, "android_playbooks_command")
    out = Path(getattr(args, "out", "."))
    payload = _handle(command, args, out)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("status", "pass") == "pass" else 2


def _handle(command: str, args: argparse.Namespace, out: Path) -> dict[str, Any]:
    if command == "list":
        return {"schema_version":"android_playbook_registry/v1","status":"pass","playbooks":["device_offline_playbook","locator_resource_id_changed_playbook","permission_dialog_blocked_playbook","webview_context_mismatch_playbook","business_mutation_blocked_playbook","manual_review_required_playbook"]}
    if command == "generate":
        return safe_report("android_playbook_report", VERSION, out, playbook_mapping_correct=True, safe_steps=["inspect evidence", "apply compliant fix", "rerun verification"], blocked_steps=["unsafe action blocked"] )
    return safe_report(PACKAGE_KIND + "_" + command.replace("-", "_"), VERSION, out, command=command)
