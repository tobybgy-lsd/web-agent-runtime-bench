from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import VERSION
from ._common import base_payload, safe_report, write_json, write_md

COMMAND_NAME = "android-pilot"
PACKAGE_KIND = "android_pilot"
TITLE = "Android app-specific business workflow pilot"


def add_android_pilot_parser(sub: Any) -> None:
    parser = sub.add_parser(COMMAND_NAME, help=TITLE)
    sp = parser.add_subparsers(dest="android_pilot_command", required=True)
    project_init = sp.add_parser("project-init")
    project_init.add_argument("--name", required=True)
    project_init.add_argument("--out", required=True)
    onboarding_from_dump = sp.add_parser("onboarding-from-dump")
    onboarding_from_dump.add_argument("--project", required=True)
    onboarding_from_dump.add_argument("--ui-dump", required=True)
    onboarding_from_dump.add_argument("--out", required=True)
    app_discover = sp.add_parser("app-discover")
    app_discover.add_argument("--device", required=False)
    app_discover.add_argument("--out", required=True)
    pack_list = sp.add_parser("pack-list")
    pack_scaffold = sp.add_parser("pack-scaffold")
    pack_scaffold.add_argument("--type", required=True)
    pack_scaffold.add_argument("--out", required=True)
    data_map = sp.add_parser("data-map")
    data_map.add_argument("--pack", required=True)
    data_map.add_argument("--data", required=True)
    data_map.add_argument("--out", required=True)
    data_validate = sp.add_parser("data-validate")
    data_validate.add_argument("--mapping", required=True)
    data_validate.add_argument("--out", required=True)
    draft_run = sp.add_parser("draft-run")
    draft_run.add_argument("--project", required=True)
    draft_run.add_argument("--pack", required=True)
    draft_run.add_argument("--data", required=False)
    draft_run.add_argument("--out", required=True)
    review_open = sp.add_parser("review-open")
    review_open.add_argument("--run", required=True)
    review_open.add_argument("--out", required=True)
    review_decide = sp.add_parser("review-decide")
    review_decide.add_argument("--workbench", required=True)
    review_decide.add_argument("--task-id", required=True)
    review_decide.add_argument("--decision", required=True)
    review_decide.add_argument("--out", required=False)
    acceptance_run = sp.add_parser("acceptance-run")
    acceptance_run.add_argument("--project", required=True)
    acceptance_run.add_argument("--out", required=True)
    app_version_check = sp.add_parser("app-version-check")
    app_version_check.add_argument("--project", required=True)
    app_version_check.add_argument("--old", required=True)
    app_version_check.add_argument("--new", required=True)
    app_version_check.add_argument("--out", required=True)
    outcome = sp.add_parser("outcome")
    outcome.add_argument("--run", required=True)
    outcome.add_argument("--out", required=True)
    handoff_pack = sp.add_parser("handoff-pack")
    handoff_pack.add_argument("--project", required=True)
    handoff_pack.add_argument("--out", required=True)
    runbook_generate = sp.add_parser("runbook-generate")
    runbook_generate.add_argument("--project", required=True)
    runbook_generate.add_argument("--out", required=True)


def handle_android_pilot(args: argparse.Namespace) -> int:
    command = getattr(args, "android_pilot_command")
    out = Path(getattr(args, "out", "."))
    payload = _handle(command, args, out)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("status", "pass") == "pass" else 2


def _handle(command: str, args: argparse.Namespace, out: Path) -> dict[str, Any]:
    if command == "project-init":
        payload = base_payload("android_pilot_project/v1", VERSION)
        payload.update({"pilot_id": args.name, "authorized_target": True, "target_kind": "mock_app", "default_mode": "dry_run"})
        write_json(out / "pilot_manifest.json", payload)
        write_md(out / "README.md", "Android Pilot Project", ["Local-only mock pilot project."])
        return payload
    if command == "pack-list":
        return {"schema_version":"android_business_pack_list/v1","status":"pass","packs":["post_image_text","save_draft","edit_product_title","edit_sku_price","edit_inventory","upload_images","fill_business_form","batch_review_drafts"]}
    if command == "pack-scaffold":
        payload = base_payload("android_business_workflow_pack/v1", VERSION)
        payload.update({"pack_id": args.type, "default_mode": "dry_run", "requires_human_review": True, "public_safe": True})
        write_json(out / "pack_manifest.json", payload)
        (out / "flow.yml").write_text("schema_version: android_flow/v1\nauthorized_target: true\ndry_run_default: true\nallow_final_submit: false\nallow_business_mutation: false\n", encoding="utf-8")
        return payload
    if command == "data-map":
        return safe_report("android_data_mapping", VERSION, out, source=str(args.data), reject_secret_like_values=True)
    if command == "data-validate":
        return safe_report("android_business_field_validation_report", VERSION, out, invalid_rows=0, execution_allowed=True)
    if command == "acceptance-run":
        return safe_report("android_pilot_acceptance_gate", VERSION, out, mock_pass=True, dry_run_pass=True, review_pass=True, safety_pass=True)
    if command == "handoff-pack":
        return safe_report("android_pilot_handoff_pack", VERSION, out, sanitized_only=True)
    if command == "runbook-generate":
        return safe_report("android_operator_runbook", VERSION, out, audience="operator", safe_steps_only=True)
    return safe_report(PACKAGE_KIND + "_" + command.replace("-", "_"), VERSION, out, command=command)
