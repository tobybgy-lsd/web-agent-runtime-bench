from __future__ import annotations

import argparse
import json
from pathlib import Path

from failure_doctor.kb.store import KnowledgeBase, render_matches_md
from failure_doctor.reasoning.report import write_reasoning_report
from failure_doctor.enterprise.ci_integration import attach_enterprise_ci
from failure_doctor.android_ops.ci_integration import write_ci_summary as write_android_ops_ci_summary
from failure_doctor.plugin.registry import read_registry

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
        if command == "diagnose":
            summary = run_ci_gate(Path(args.project), Path(args.out), fail_on=str(args.fail_on))
            if getattr(args, "kb", None):
                _attach_kb_summary(Path(args.kb), Path(args.project), Path(args.out))
            if getattr(args, "hybrid_reasoning", False):
                _attach_hybrid_reasoning(Path(args.out), str(getattr(args, "reasoner", "mock_reasoner")))
            if getattr(args, "enterprise_workspace", None):
                attach_enterprise_ci(Path(args.out), Path(args.enterprise_workspace))
            if getattr(args, "plugins", None):
                _attach_plugin_summary(Path(args.plugins), Path(args.out))
            if getattr(args, "include_android_ops", False):
                _attach_android_ops_summary(Path(args.out))
            gate = summary["gate"]
            print("Agent Failure Doctor CI Diagnosis")
            print(f"Decision: {gate.get('decision')}")
            print(f"Output: {args.out}")
            return 0 if gate.get("decision") == "pass" else 3
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("unknown ci command")
    return 2


def _attach_kb_summary(kb_path: Path, report_or_project: Path, out: Path) -> None:
    try:
        result = KnowledgeBase(kb_path).match_report(report_or_project)
    except (FileNotFoundError, ValueError):
        return
    (out / "similar_cases.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "similar_cases.md").write_text(render_matches_md(result), encoding="utf-8")
    summary_path = out / "ci_summary.md"
    if summary_path.exists():
        with summary_path.open("a", encoding="utf-8") as handle:
            handle.write("\n## Similar Historical Cases\n\n")
            if not result.get("matches"):
                handle.write("No similar local KB case found.\n")
            for item in result.get("matches", [])[:5]:
                handle.write(
                    f"- `{item['case_id']}` score `{item['score']}` "
                    f"{item.get('failure_type')} / {item.get('subtype')} "
                    f"verified_fix_available={item.get('verified_fix_available')}\n"
                )


def _attach_hybrid_reasoning(out: Path, provider: str) -> None:
    try:
        result = write_reasoning_report(out, out / "hybrid_reasoning", provider=provider)
    except (FileNotFoundError, ValueError, OSError):
        return
    summary_path = out / "ci_summary.md"
    if summary_path.exists():
        with summary_path.open("a", encoding="utf-8") as handle:
            handle.write("\n## Hybrid Reasoning\n\n")
            handle.write(f"- Status: `{result.get('reasoning_status')}`\n")
            handle.write(f"- Provider: `{result.get('provider')}`\n")
            handle.write("- Report: `hybrid_reasoning/hybrid_reasoning_report.json`\n")


def _attach_plugin_summary(plugin_workspace: Path, out: Path) -> None:
    try:
        registry = read_registry(plugin_workspace)
    except (FileNotFoundError, ValueError, OSError):
        return
    summary = {
        "schema_version": "ci_plugin_summary/v1",
        "plugin_count": len(registry.get("plugins", [])),
        "enabled_plugins": [
            {
                "plugin_id": item.get("plugin_id"),
                "type": item.get("type"),
                "validation_status": item.get("validation_status"),
                "risk_level": item.get("risk_level"),
            }
            for item in registry.get("plugins", [])
            if item.get("status") == "enabled"
        ],
        "sanitized_only": True,
        "external_api_call_count": 0,
    }
    (out / "plugin_ci_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary_path = out / "ci_summary.md"
    if summary_path.exists():
        with summary_path.open("a", encoding="utf-8") as handle:
            handle.write("\n## Plugin Summary\n\n")
            for item in summary["enabled_plugins"]:
                handle.write(
                    f"- `{item['plugin_id']}` `{item['type']}` "
                    f"validation `{item['validation_status']}` risk `{item['risk_level']}`\n"
                )


def _attach_android_ops_summary(out: Path) -> None:
    summary = write_android_ops_ci_summary(out / "android_ops")
    summary_path = out / "ci_summary.md"
    if summary_path.exists():
        with summary_path.open("a", encoding="utf-8") as handle:
            handle.write("\n## Android Ops\n\n")
            handle.write(f"- Status: `{summary.get('status')}`\n")
            handle.write("- Mode: local-only dry-run validation; no real device or Appium startup by default.\n")
            handle.write("- Report: `android_ops/android_ops_ci_summary.json`\n")
