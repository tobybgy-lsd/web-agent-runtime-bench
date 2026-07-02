from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    apply_retention,
    backup_workspace,
    disaster_recovery_drill,
    health_report,
    migrate_workspace,
    offline_bundle,
    restore_workspace,
    rotate_logs,
    security_posture,
    snapshot_config,
)


def add_deploy_parser(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    deploy = sub.add_parser("deploy", help="Enterprise deployment hardening utilities")
    deploy_sub = deploy.add_subparsers(dest="deploy_command", required=True)
    health = deploy_sub.add_parser("health")
    health.add_argument("--workspace", required=True)
    health.add_argument("--out", required=True)
    backup = deploy_sub.add_parser("backup")
    backup.add_argument("--workspace", required=True)
    backup.add_argument("--out", required=True)
    restore = deploy_sub.add_parser("restore")
    restore.add_argument("--backup", required=True)
    restore.add_argument("--out", required=True)
    migrate = deploy_sub.add_parser("migrate")
    migrate.add_argument("--workspace", required=True)
    migrate.add_argument("--from", dest="from_version", required=True)
    migrate.add_argument("--to", dest="to_version", required=True)
    snap = deploy_sub.add_parser("snapshot-config")
    snap.add_argument("--workspace", required=True)
    snap.add_argument("--out", required=True)
    retention = deploy_sub.add_parser("retention-apply")
    retention.add_argument("--workspace", required=True)
    retention.add_argument("--policy", required=True)
    rotate = deploy_sub.add_parser("log-rotate")
    rotate.add_argument("--workspace", required=True)
    offline = deploy_sub.add_parser("offline-bundle")
    offline.add_argument("--out", required=True)
    dr = deploy_sub.add_parser("disaster-recovery-drill")
    dr.add_argument("--workspace", required=True)
    dr.add_argument("--out", required=True)
    posture = deploy_sub.add_parser("security-posture")
    posture.add_argument("--workspace", required=True)
    posture.add_argument("--out", required=True)


def handle_deploy(args: argparse.Namespace) -> int:
    try:
        command = args.deploy_command
        if command == "health":
            result = health_report(Path(args.workspace), Path(args.out))
        elif command == "backup":
            result = backup_workspace(Path(args.workspace), Path(args.out))
        elif command == "restore":
            result = restore_workspace(Path(args.backup), Path(args.out))
        elif command == "migrate":
            result = migrate_workspace(Path(args.workspace), args.from_version, args.to_version)
        elif command == "snapshot-config":
            result = snapshot_config(Path(args.workspace), Path(args.out))
        elif command == "retention-apply":
            result = apply_retention(Path(args.workspace), Path(args.policy))
        elif command == "log-rotate":
            result = rotate_logs(Path(args.workspace))
        elif command == "offline-bundle":
            result = offline_bundle(Path(args.out))
        elif command == "disaster-recovery-drill":
            result = disaster_recovery_drill(Path(args.workspace), Path(args.out))
        elif command == "security-posture":
            result = security_posture(Path(args.workspace), Path(args.out))
        else:
            print("unknown deploy command")
            return 2
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
