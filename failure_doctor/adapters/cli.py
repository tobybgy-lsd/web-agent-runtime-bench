from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import diagnose_adapter_input, normalize_adapter_input


def add_adapter_parser(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    adapter = sub.add_parser("adapter", help="Normalize and diagnose RPA/API/mobile automation artifacts")
    adapter_sub = adapter.add_subparsers(dest="adapter_command", required=True)
    for kind in ("rpa", "api", "mobile"):
        kind_parser = adapter_sub.add_parser(kind, help=f"{kind.upper()} adapter commands")
        kind_sub = kind_parser.add_subparsers(dest=f"{kind}_command", required=True)
        normalize = kind_sub.add_parser("normalize", help=f"Normalize {kind} logs into adapter evidence")
        normalize.add_argument("--input", required=True)
        normalize.add_argument("--out", required=True)
        diagnose = kind_sub.add_parser("diagnose", help=f"Diagnose {kind} logs with public-safe rules")
        diagnose.add_argument("--input", required=True)
        diagnose.add_argument("--out", required=True)


def handle_adapter(args: argparse.Namespace) -> int:
    kind = str(args.adapter_command)
    command = getattr(args, f"{kind}_command")
    try:
        if command == "normalize":
            result = normalize_adapter_input(Path(args.input), Path(args.out), kind=kind)
        elif command == "diagnose":
            result = diagnose_adapter_input(Path(args.input), Path(args.out), kind=kind)
        else:
            print("unknown adapter command")
            return 2
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
