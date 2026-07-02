from __future__ import annotations

import json
from pathlib import Path
import tempfile
from typing import Any

from .app_profile import create_app_profile, validate_app_profile
from .console_integration import android_pro_console_summary
from .device_matrix import run_device_matrix
from .failure_replay_pack import create_failure_replay_pack
from .flow_compiler import compile_flow
from .flow_linter import lint_flow_file
from .flow_templates import scaffold_template
from .locator_registry import build_locator_registry, validate_locator_registry
from .locator_self_healing import recommend_locator_heal
from .page_object_generator import generate_page_objects
from .stability_score import score_android_run
from .task_queue import init_queue, run_queue
from .ui_tree_diff import diff_ui_trees
from .validation import run_onboarding_check


def add_android_pro_parser(sub: Any) -> None:
    android = sub.add_parser(
        "android-pro",
        help="Local-only Android APK production-hardening workflow tools",
    )
    android_sub = android.add_subparsers(dest="android_pro_command", required=True)

    profile = android_sub.add_parser("profile", help="Create, validate, or inspect Android app profiles")
    profile_sub = profile.add_subparsers(dest="profile_command", required=True)
    profile_init = profile_sub.add_parser("init", help="Create an authorized dry-run app profile")
    profile_init.add_argument("--package", required=True)
    profile_init.add_argument("--out", required=True)
    profile_init.add_argument("--app-label", default="Mock Android App")
    profile_validate = profile_sub.add_parser("validate", help="Validate an app profile")
    profile_validate.add_argument("--profile", required=True)
    profile_inspect = profile_sub.add_parser("inspect", help="Inspect and write app profile validation output")
    profile_inspect.add_argument("--profile", required=True)
    profile_inspect.add_argument("--out", required=True)

    page = android_sub.add_parser("page-object", help="Generate page object metadata from a UI dump")
    page_sub = page.add_subparsers(dest="page_command", required=True)
    page_generate = page_sub.add_parser("generate", help="Generate local page object JSON")
    page_generate.add_argument("--ui-dump", required=True)
    page_generate.add_argument("--out", required=True)

    registry = android_sub.add_parser("locator-registry", help="Build or validate locator registry files")
    registry_sub = registry.add_subparsers(dest="registry_command", required=True)
    registry_build = registry_sub.add_parser("build", help="Build a registry from a UI dump")
    registry_build.add_argument("--ui-dump", required=True)
    registry_build.add_argument("--out", required=True)
    registry_validate = registry_sub.add_parser("validate", help="Validate a registry")
    registry_validate.add_argument("--registry", required=True)

    heal = android_sub.add_parser("locator-heal", help="Recommend locator healing candidates without auto-applying them")
    heal.add_argument("--old-ui", required=True)
    heal.add_argument("--new-ui", required=True)
    heal.add_argument("--failed-locator", required=True)
    heal.add_argument("--out", required=True)

    diff = android_sub.add_parser("ui-diff", help="Diff two Android UI tree dumps")
    diff.add_argument("--old", required=True)
    diff.add_argument("--new", required=True)
    diff.add_argument("--out", required=True)

    flow = android_sub.add_parser("flow", help="Compile, lint, or scaffold dry-run Android workflow templates")
    flow_sub = flow.add_subparsers(dest="flow_command", required=True)
    flow_compile = flow_sub.add_parser("compile", help="Compile a flow into a safe executable plan")
    flow_compile.add_argument("--flow", required=True)
    flow_compile.add_argument("--profile", required=True)
    flow_compile.add_argument("--out", required=True)
    flow_lint = flow_sub.add_parser("lint", help="Lint an Android flow")
    flow_lint.add_argument("--flow", required=True)
    flow_lint.add_argument("--profile", default=None)
    flow_lint.add_argument("--out", required=True)
    flow_scaffold = flow_sub.add_parser("scaffold", help="Copy a safe template flow")
    flow_scaffold.add_argument("--template", required=True)
    flow_scaffold.add_argument("--out", required=True)

    matrix = android_sub.add_parser("matrix", help="Run a mock local device matrix")
    matrix_sub = matrix.add_subparsers(dest="matrix_command", required=True)
    matrix_run = matrix_sub.add_parser("run", help="Run matrix validation for a flow")
    matrix_run.add_argument("--matrix", required=True)
    matrix_run.add_argument("--flow", required=True)
    matrix_run.add_argument("--out", required=True)

    queue = android_sub.add_parser("queue", help="Initialize or run a local task queue")
    queue_sub = queue.add_subparsers(dest="queue_command", required=True)
    queue_init = queue_sub.add_parser("init", help="Create a queue manifest")
    queue_init.add_argument("--out", required=True)
    queue_run = queue_sub.add_parser("run", help="Run a queue in dry-run mode")
    queue_run.add_argument("--queue", required=True)
    queue_run.add_argument("--flow", required=True)
    queue_run.add_argument("--out", required=True)

    replay = android_sub.add_parser("replay-pack", help="Create a sanitized failure replay pack")
    replay_sub = replay.add_subparsers(dest="replay_command", required=True)
    replay_create = replay_sub.add_parser("create", help="Create replay pack metadata")
    replay_create.add_argument("--run", required=True)
    replay_create.add_argument("--out", required=True)

    stability = android_sub.add_parser("stability-score", help="Compute Android workflow stability score")
    stability.add_argument("--run", required=True)
    stability.add_argument("--out", required=True)

    onboarding = android_sub.add_parser("onboarding-check", help="Run local onboarding checks")
    onboarding.add_argument("--profile", required=True)
    onboarding.add_argument("--flow", required=True)
    onboarding.add_argument("--out", required=True)

    console = android_sub.add_parser("console-summary", help="Write a local console integration summary")
    console.add_argument("--profile", required=True)
    console.add_argument("--flow", required=True)
    console.add_argument("--out", required=True)


def handle_android_pro(args: Any) -> int:
    command = args.android_pro_command
    if command == "profile":
        if args.profile_command == "init":
            payload = create_app_profile(args.package, Path(args.out), app_label=args.app_label)
            print(f"Android Pro profile created: {payload['package_name']}")
            return 0
        payload = validate_app_profile(Path(args.profile))
        if args.profile_command == "inspect":
            _write(Path(args.out), payload)
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("status") == "pass" else 2
    if command == "page-object":
        payload = generate_page_objects(Path(args.ui_dump), Path(args.out))
        print(f"Android Pro page objects: {payload.get('page_count')}")
        return 0
    if command == "locator-registry":
        if args.registry_command == "build":
            payload = build_locator_registry(Path(args.ui_dump), Path(args.out))
            print(f"Android Pro locator registry entries: {payload.get('locator_count')}")
            return 0
        payload = validate_locator_registry(Path(args.registry))
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("status") == "pass" else 2
    if command == "locator-heal":
        failed = Path(args.failed_locator)
        if failed.exists():
            payload = recommend_locator_heal(Path(args.old_ui), Path(args.new_ui), failed, Path(args.out))
        else:
            with tempfile.TemporaryDirectory() as tmp_name:
                locator_file = Path(tmp_name) / "failed_locator.json"
                _write(locator_file, {"strategy": "resource-id", "value": args.failed_locator})
                payload = recommend_locator_heal(Path(args.old_ui), Path(args.new_ui), locator_file, Path(args.out))
        print(f"Android Pro locator candidates: {len(payload.get('candidates', []))}")
        return 0
    if command == "ui-diff":
        payload = diff_ui_trees(Path(args.old), Path(args.new), Path(args.out))
        print(f"Android Pro UI diff changes: {payload.get('change_count')}")
        return 0
    if command == "flow":
        if args.flow_command == "compile":
            payload = compile_flow(Path(args.flow), Path(args.profile), Path(args.out))
        elif args.flow_command == "lint":
            payload = lint_flow_file(Path(args.flow), Path(args.profile) if args.profile else None, Path(args.out))
        else:
            payload = scaffold_template(args.template, Path(args.out))
        print(json.dumps({"status": payload.get("status"), "schema_version": payload.get("schema_version")}, ensure_ascii=False))
        return 0 if payload.get("status") == "pass" else 2
    if command == "matrix" and args.matrix_command == "run":
        payload = run_device_matrix(Path(args.matrix), Path(args.flow), Path(args.out))
        print(f"Android Pro matrix: {payload.get('status')}")
        return 0 if payload.get("status") == "pass" else 2
    if command == "queue":
        if args.queue_command == "init":
            payload = init_queue(Path(args.out))
        else:
            payload = run_queue(Path(args.queue), Path(args.flow), Path(args.out))
        print(f"Android Pro queue: {payload.get('status')}")
        return 0 if payload.get("status") in {"pass", "ready"} else 2
    if command == "replay-pack" and args.replay_command == "create":
        payload = create_failure_replay_pack(Path(args.run), Path(args.out))
        print(f"Android Pro replay pack: {payload.get('status')}")
        return 0 if payload.get("status") == "pass" else 2
    if command == "stability-score":
        payload = score_android_run(Path(args.run), Path(args.out))
        print(f"Android Pro stability score: {payload.get('overall_android_stability_score')}")
        return 0
    if command == "onboarding-check":
        payload = run_onboarding_check(Path(args.profile), Path(args.flow), Path(args.out))
        print(f"Android Pro onboarding: {payload.get('status')}")
        return 0 if payload.get("status") == "pass" else 2
    if command == "console-summary":
        payload = android_pro_console_summary()
        payload.update({"profile": str(Path(args.profile)), "flow": str(Path(args.flow))})
        _write(Path(args.out), payload)
        print(f"Android Pro console summary: {payload.get('status')}")
        return 0 if payload.get("status") == "pass" else 2
    return 1


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
