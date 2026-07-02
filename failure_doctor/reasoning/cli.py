from __future__ import annotations

import argparse
import json
from pathlib import Path

from .report import write_reasoning_report


def add_reasoning_parsers(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    reason = sub.add_parser("reason", help="Generate evidence-bound local hybrid reasoning")
    reason.add_argument("reason_action", nargs="?", choices=["validate", "explain"], help="Optional reasoning utility")
    reason.add_argument("--input", required=True, help="Input report directory or reasoning report")
    reason.add_argument("--out", default=None, help="Output reasoning report directory")
    reason.add_argument("--provider", default="mock_reasoner", choices=["mock_reasoner", "ollama_local", "llama_cpp_local", "imported_reasoning"])
    reason.add_argument("--model", default=None)
    reason.add_argument("--model-path", default=None)
    reason.add_argument("--reasoning-json", default=None)
    reason.add_argument("--claim-id", default=None)

    root = sub.add_parser("root-cause", help="Generate an evidence-bound root cause graph")
    root.add_argument("--input", required=True)
    root.add_argument("--out", required=True)
    root.add_argument("--provider", default="mock_reasoner")

    chain = sub.add_parser("causal-chain", help="Generate an evidence-bound causal chain")
    chain.add_argument("--input", required=True)
    chain.add_argument("--out", required=True)
    chain.add_argument("--provider", default="mock_reasoner")


def handle_reasoning_command(args: argparse.Namespace) -> int:
    command = getattr(args, "command", "")
    if command == "reason":
        if getattr(args, "reason_action", None) == "validate":
            payload = json.loads((Path(args.input) / "reasoning_validation.json").read_text(encoding="utf-8"))
            print(f"Reasoning validation: {payload.get('status')}")
            return 0 if payload.get("status") == "pass" else 3
        if getattr(args, "reason_action", None) == "explain":
            report = json.loads((Path(args.input) / "hybrid_reasoning_report.json").read_text(encoding="utf-8"))
            claim_id = getattr(args, "claim_id", None)
            for claim in report.get("claims", []):
                if claim.get("claim_id") == claim_id:
                    print(json.dumps(claim, indent=2, ensure_ascii=False))
                    return 0
            print("claim not found")
            return 1
        out = Path(args.out or "reasoning_report")
        report = write_reasoning_report(
            Path(args.input),
            out,
            provider=str(args.provider),
            model=getattr(args, "model", None),
            model_path=getattr(args, "model_path", None),
            reasoning_json=Path(args.reasoning_json) if getattr(args, "reasoning_json", None) else None,
        )
        print("Agent Failure Doctor Hybrid Reasoning")
        print(f"Status: {report.get('reasoning_status')}")
        print(f"Provider: {report.get('provider')}")
        print(f"Output: {out}")
        return 0 if report.get("reasoning_status") == "validated" else 3
    if command in {"root-cause", "causal-chain"}:
        report = write_reasoning_report(Path(args.input), Path(args.out), provider=str(getattr(args, "provider", "mock_reasoner")))
        print(f"Agent Failure Doctor {command}")
        print(f"Status: {report.get('reasoning_status')}")
        print(f"Output: {args.out}")
        return 0 if report.get("reasoning_status") == "validated" else 3
    return 2
