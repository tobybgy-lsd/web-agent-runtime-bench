from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .appium_orchestrator import plan_appium_sessions
from .business_data_binding import bind_data
from .business_templates import list_templates, scaffold_template
from .ci_integration import write_ci_summary
from .compatibility_report import generate_compatibility_report
from .console_integration import android_ops_console_summary
from .device_farm import farm_status, init_farm
from .device_health import check_device_health
from .device_inventory import discover_devices
from .device_lease import lease_device, release_device
from .device_recovery import recover_device
from .enterprise_integration import validate_enterprise_policy
from .flaky_detector import detect_flaky
from .mutation_guard import evaluate_mutation_guard
from .ops_dashboard import write_dashboard_summary
from .ops_metrics import generate_metrics
from .real_device_replay import replay_run
from .session_manager import start_session, stop_session
from .workflow_runbook import generate_runbook
from .workflow_scheduler import plan_schedule, run_schedule


def add_android_ops_parser(sub: Any) -> None:
    parser = sub.add_parser("android-ops", help="Local-only Android real device farm and business workflow ops")
    ops = parser.add_subparsers(dest="android_ops_command", required=True)

    farm = ops.add_parser("farm", help="Manage a local Android device farm")
    farm_sub = farm.add_subparsers(dest="farm_command", required=True)
    farm_init = farm_sub.add_parser("init")
    farm_init.add_argument("--out", required=True)
    farm_discover = farm_sub.add_parser("discover")
    farm_discover.add_argument("--farm", required=True)
    farm_discover.add_argument("--out", required=True)
    farm_status_cmd = farm_sub.add_parser("status")
    farm_status_cmd.add_argument("--farm", required=True)

    device = ops.add_parser("device", help="Check, lease, release, or recover devices")
    device_sub = device.add_subparsers(dest="device_command", required=True)
    health = device_sub.add_parser("health")
    health.add_argument("--device", required=True)
    health.add_argument("--out", required=True)
    health.add_argument("--farm", default=None)
    lease = device_sub.add_parser("lease")
    lease.add_argument("--farm", required=True)
    lease.add_argument("--device", required=True)
    lease.add_argument("--task-id", required=True)
    release = device_sub.add_parser("release")
    release.add_argument("--farm", required=True)
    release.add_argument("--device", required=True)
    release.add_argument("--task-id", required=True)
    recover = device_sub.add_parser("recover")
    recover.add_argument("--device", required=True)
    recover.add_argument("--strategy", default="soft-reset")
    recover.add_argument("--out", required=True)

    appium = ops.add_parser("appium")
    appium_sub = appium.add_subparsers(dest="appium_command", required=True)
    appium_plan = appium_sub.add_parser("plan")
    appium_plan.add_argument("--farm", required=True)
    appium_plan.add_argument("--out", required=True)
    appium_start = appium_sub.add_parser("start-session")
    appium_start.add_argument("--device", required=True)
    appium_start.add_argument("--port", type=int, required=True)
    appium_start.add_argument("--out", required=True)
    appium_stop = appium_sub.add_parser("stop-session")
    appium_stop.add_argument("--session", required=True)

    template = ops.add_parser("template")
    template_sub = template.add_subparsers(dest="template_command", required=True)
    template_sub.add_parser("list")
    template_scaffold = template_sub.add_parser("scaffold")
    template_scaffold.add_argument("--type", required=True)
    template_scaffold.add_argument("--out", required=True)

    data = ops.add_parser("data")
    data_sub = data.add_subparsers(dest="data_command", required=True)
    bind = data_sub.add_parser("bind")
    bind.add_argument("--flow", required=True)
    bind.add_argument("--data", required=True)
    bind.add_argument("--out", required=True)

    scheduler = ops.add_parser("scheduler")
    scheduler_sub = scheduler.add_subparsers(dest="scheduler_command", required=True)
    sched_plan = scheduler_sub.add_parser("plan")
    sched_plan.add_argument("--farm", required=True)
    sched_plan.add_argument("--queue", required=True)
    sched_plan.add_argument("--out", required=True)
    sched_run = scheduler_sub.add_parser("run")
    sched_run.add_argument("--plan", required=True)
    sched_run.add_argument("--out", required=True)

    replay = ops.add_parser("replay")
    replay.add_argument("--run", required=True)
    replay.add_argument("--device", required=True)
    replay.add_argument("--out", required=True)

    flaky = ops.add_parser("flaky")
    flaky_sub = flaky.add_subparsers(dest="flaky_command", required=True)
    flaky_detect = flaky_sub.add_parser("detect")
    flaky_detect.add_argument("--runs", required=True)
    flaky_detect.add_argument("--out", required=True)

    compat = ops.add_parser("compatibility")
    compat.add_argument("--runs", required=True)
    compat.add_argument("--out", required=True)

    runbook = ops.add_parser("runbook")
    runbook_sub = runbook.add_subparsers(dest="runbook_command", required=True)
    runbook_gen = runbook_sub.add_parser("generate")
    runbook_gen.add_argument("--run", required=True)
    runbook_gen.add_argument("--out", required=True)

    metrics = ops.add_parser("metrics")
    metrics.add_argument("--runs", required=True)
    metrics.add_argument("--out", required=True)

    mutation = ops.add_parser("mutation-check")
    mutation.add_argument("--flow", required=True)
    mutation.add_argument("--out", required=True)

    dashboard = ops.add_parser("dashboard")
    dashboard.add_argument("--out", required=True)
    dashboard.add_argument("--farm", default=None)

    ci = ops.add_parser("ci-summary")
    ci.add_argument("--out", required=True)

    enterprise = ops.add_parser("enterprise-policy")
    enterprise.add_argument("--out", required=True)

    console = ops.add_parser("console-summary")
    console.add_argument("--out", required=True)


def handle_android_ops(args: Any) -> int:
    command = args.android_ops_command
    if command == "farm":
        if args.farm_command == "init":
            payload = init_farm(Path(args.out))
        elif args.farm_command == "discover":
            payload = discover_devices(Path(args.farm), Path(args.out))
        else:
            payload = farm_status(Path(args.farm))
        _print(payload)
        return 0 if payload.get("status", "pass") in {"pass", "missing"} else 2
    if command == "device":
        if args.device_command == "health":
            payload = check_device_health(args.device, Path(args.out), Path(args.farm) if args.farm else None)
        elif args.device_command == "lease":
            payload = lease_device(Path(args.farm), args.device, args.task_id)
        elif args.device_command == "release":
            payload = release_device(Path(args.farm), args.device, args.task_id)
        else:
            payload = recover_device(args.device, args.strategy, Path(args.out))
        _print(payload)
        return 0 if payload.get("status") in {"pass", "healthy", "not_found"} else 2
    if command == "appium":
        if args.appium_command == "plan":
            payload = plan_appium_sessions(Path(args.farm), Path(args.out))
        elif args.appium_command == "start-session":
            payload = start_session(args.device, args.port, Path(args.out))
        else:
            payload = stop_session(Path(args.session))
        _print(payload)
        return 0
    if command == "template":
        payload = list_templates() if args.template_command == "list" else scaffold_template(args.type, Path(args.out))
        _print(payload)
        return 0
    if command == "data":
        payload = bind_data(Path(args.flow), Path(args.data), Path(args.out))
        _print(payload)
        return 0 if payload.get("status") == "pass" else 2
    if command == "scheduler":
        payload = plan_schedule(Path(args.farm), Path(args.queue), Path(args.out)) if args.scheduler_command == "plan" else run_schedule(Path(args.plan), Path(args.out))
        _print(payload)
        return 0
    if command == "replay":
        _print(replay_run(Path(args.run), args.device, Path(args.out)))
        return 0
    if command == "flaky":
        _print(detect_flaky(Path(args.runs), Path(args.out)))
        return 0
    if command == "compatibility":
        _print(generate_compatibility_report(Path(args.runs), Path(args.out)))
        return 0
    if command == "runbook":
        _print(generate_runbook(Path(args.run), Path(args.out)))
        return 0
    if command == "metrics":
        _print(generate_metrics(Path(args.runs), Path(args.out)))
        return 0
    if command == "mutation-check":
        payload = evaluate_mutation_guard(Path(args.flow), Path(args.out))
        _print(payload)
        return 0
    if command == "dashboard":
        _print(write_dashboard_summary(Path(args.out), Path(args.farm) if args.farm else None))
        return 0
    if command == "ci-summary":
        _print(write_ci_summary(Path(args.out)))
        return 0
    if command == "enterprise-policy":
        _print(validate_enterprise_policy(Path(args.out)))
        return 0
    if command == "console-summary":
        payload = android_ops_console_summary()
        from .ops_audit import write_json

        write_json(Path(args.out) / "android_ops_console_summary.json", payload)
        _print(payload)
        return 0
    return 1


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))

