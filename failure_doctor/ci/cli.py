from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import run_ci_gate, validate_ci_report, write_ci_templates


def handle_ci(args: argparse.Namespace) -> int:
    command = getattr(args, "ci_command", None)
    try:
        if command == "run":
            summary = run_ci_gate(Path(args.input), Path(args.out), fail_on=str(args.fail_on))
            gate = summary["gate"]
            print("Agent Failure Doctor CI Gate")
            print(f"Decision: {gate.get('decision')}")
            print(f"Severity: {summary['severity'].get('severity')}")
            print(f"Output: {args.out}")
            return 0 if gate.get("decision") == "pass" else 3
        if command == "templates":
            result = write_ci_templates(Path(args.out))
            print("Agent Failure Doctor CI Templates")
            print(f"Templates: {result.get('template_count')}")
            print(f"Output: {args.out}")
            return 0
        if command == "validate":
            result = validate_ci_report(Path(args.input))
            out = Path(args.out)
            out.mkdir(parents=True, exist_ok=True)
            (out / "ci_validation.json").write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print("Agent Failure Doctor CI Validation")
            print(f"Status: {result.get('status')}")
            print(f"Output: {out}")
            return 0 if result.get("status") == "pass" else 3
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("unknown ci command")
    return 2
