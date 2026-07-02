from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import VERSION
from ._common import base_payload, safe_report, write_json, write_md

COMMAND_NAME = "android-lab"
PACKAGE_KIND = "android_lab"
TITLE = "Android device lab hardening"


def add_android_lab_parser(sub: Any) -> None:
    parser = sub.add_parser(COMMAND_NAME, help=TITLE)
    sp = parser.add_subparsers(dest="android_lab_command", required=True)
    init = sp.add_parser("init")
    init.add_argument("--out", required=True)
    daily_health = sp.add_parser("daily-health")
    daily_health.add_argument("--lab", required=True)
    daily_health.add_argument("--out", required=True)
    long_run = sp.add_parser("long-run")
    long_run.add_argument("--lab", required=True)
    long_run.add_argument("--duration-minutes", required=False)
    long_run.add_argument("--out", required=True)
    recovery_metrics = sp.add_parser("recovery-metrics")
    recovery_metrics.add_argument("--lab", required=True)
    recovery_metrics.add_argument("--out", required=True)
    trend = sp.add_parser("trend")
    trend.add_argument("--lab", required=True)
    trend.add_argument("--out", required=True)
    utilization = sp.add_parser("utilization")
    utilization.add_argument("--lab", required=True)
    utilization.add_argument("--out", required=True)
    flaky_report = sp.add_parser("flaky-report")
    flaky_report.add_argument("--lab", required=True)
    flaky_report.add_argument("--out", required=True)
    runbook = sp.add_parser("runbook")
    runbook.add_argument("--lab", required=True)
    runbook.add_argument("--out", required=True)


def handle_android_lab(args: argparse.Namespace) -> int:
    command = getattr(args, "android_lab_command")
    out = Path(getattr(args, "out", "."))
    payload = _handle(command, args, out)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("status", "pass") == "pass" else 2


def _handle(command: str, args: argparse.Namespace, out: Path) -> dict[str, Any]:
    if command == "init":
        payload = base_payload("android_lab_workspace/v1", VERSION)
        payload.update({"mock_lab": True, "devices": []})
        write_json(out / "android_lab_workspace.json", payload)
        return payload
    return safe_report(PACKAGE_KIND + "_" + command.replace("-", "_"), VERSION, out, command=command)
