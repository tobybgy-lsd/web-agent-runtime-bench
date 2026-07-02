from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    check_api,
    check_plugin_abi,
    check_schema,
    compatibility_report,
    deprecation_report,
    migration_guide,
)


def add_stability_parser(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    stability = sub.add_parser("stability", help="Check stable CLI, schema, and plugin ABI contracts")
    stability_sub = stability.add_subparsers(dest="stability_command", required=True)
    api = stability_sub.add_parser("check-api")
    api.add_argument("--out", required=True)
    schema = stability_sub.add_parser("check-schema")
    schema.add_argument("--out", required=True)
    abi = stability_sub.add_parser("check-plugin-abi")
    abi.add_argument("--out", required=True)
    compat = stability_sub.add_parser("compatibility")
    compat.add_argument("--from", dest="from_version", required=True)
    compat.add_argument("--to", dest="to_version", required=True)
    compat.add_argument("--out", required=True)
    dep = stability_sub.add_parser("deprecation-report")
    dep.add_argument("--out", required=True)
    mig = stability_sub.add_parser("migration-guide")
    mig.add_argument("--from", dest="from_version", required=True)
    mig.add_argument("--to", dest="to_version", required=True)
    mig.add_argument("--out", required=True)


def handle_stability(args: argparse.Namespace) -> int:
    command = args.stability_command
    if command == "check-api":
        result = check_api(Path(args.out))
    elif command == "check-schema":
        result = check_schema(Path(args.out))
    elif command == "check-plugin-abi":
        result = check_plugin_abi(Path(args.out))
    elif command == "compatibility":
        result = compatibility_report(args.from_version, args.to_version, Path(args.out))
    elif command == "deprecation-report":
        result = deprecation_report(Path(args.out))
    elif command == "migration-guide":
        result = migration_guide(args.from_version, args.to_version, Path(args.out))
    else:
        print("unknown stability command")
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
