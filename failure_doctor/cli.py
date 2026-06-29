from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from zipfile import ZIP_DEFLATED, ZipFile

from failure_doctor.batch import discover_runs, write_batch_report
from failure_doctor.ai_handoff import write_ai_handoff_pack, write_patch_proposal
from failure_doctor.auto_collect import collect_project, watch_project
from failure_doctor.run_capture import capture_run, write_shareable_zip
from failure_doctor.sanitize_share import sanitize_failure_pack
from integrations.cross_framework.common import SUPPORTED_FRAMEWORKS, normalize_framework_failure
from integrations.generic_log_pack.adapter import pack_generic_logs
from integrations.playwright.collector import collect_playwright_artifacts
from tools.failure_artifacts.adapters import artifact_from_playwright_trace
from tools.failure_artifacts.composite import classify_composite_failure_artifact
from tools.failure_artifacts.diagnose import diagnose_artifact
from tools.failure_artifacts.issue import render_issue_draft
from tools.failure_artifacts.reporter import render_markdown_report
from tools.failure_artifacts.regression_case import create_regression_case
from tools.failure_artifacts.resolution import (
    generate_fix_plan,
    render_fix_plan_markdown,
    render_verification_markdown,
    verify_resolution,
    write_json,
)
from trace_doctor.cli import _render_repair_suggestions


NEXT_ACTION = "把 codex_fix_prompt.md 交给 Codex/Claude 修改代码"


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "diagnose":
        return diagnose_inputs(args)
    if args.command == "plan":
        return plan_from_report(args)
    if args.command == "verify":
        return verify_inputs(args)
    if args.command == "collect-playwright":
        return collect_playwright_inputs(args)
    if args.command == "collect":
        return collect_project_inputs(args)
    if args.command == "watch":
        return watch_project_inputs(args)
    if args.command == "adapt":
        return adapt_framework_inputs(args)
    if args.command == "pack-logs":
        return pack_log_inputs(args)
    if args.command == "sanitize":
        return sanitize_inputs(args)
    if args.command == "run":
        return run_command(args)
    if args.command == "handoff":
        return handoff_report(args)
    if args.command == "propose-patch":
        return propose_patch(args)
    if args.command == "batch":
        return batch_diagnose(args)
    parser.print_help()
    return 1


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="failure_doctor",
        description="Agent Failure Doctor: diagnose local AI automation failures from traces, logs, network captures, and descriptions.",
    )
    sub = parser.add_subparsers(dest="command")
    diagnose = sub.add_parser("diagnose", help="Diagnose a local failure input file or directory")
    diagnose.add_argument("input", help="Path to trace.zip, log file, network.json, description file, screenshot, or a directory")
    diagnose.add_argument("--out", required=True, help="Output report directory")
    diagnose.add_argument("--run-id", default=None, help="Stable run identifier")
    plan = sub.add_parser("plan", help="Generate a fix plan from a diagnosis report directory")
    plan.add_argument("report", help="Path to a report directory containing diagnosis.json")
    plan.add_argument("--out", required=True, help="Output fix plan directory")
    verify = sub.add_parser("verify", help="Verify whether a fix resolved a before/after failure")
    verify.add_argument("--before", required=True, help="Before input directory/file or report directory")
    verify.add_argument("--after", required=True, help="After input directory/file or report directory")
    verify.add_argument("--out", required=True, help="Output verification report directory")
    verify.add_argument("--fix-plan", default=None, help="Optional fix_plan.json path or directory")
    verify.add_argument("--create-regression", action="store_true", help="Write regression_case.json")
    collect = sub.add_parser("collect-playwright", help="Collect Playwright test-results into a failure pack")
    collect.add_argument("test_results", help="Path to Playwright test-results or a failed test artifact folder")
    collect.add_argument("--out", required=True, help="Output failure pack directory")
    auto_collect = sub.add_parser("collect", help="Collect local project failure evidence into a one-click diagnosis pack")
    auto_collect.add_argument("--project", required=True, help="Authorized project folder to collect from")
    auto_collect.add_argument(
        "--preset",
        default="auto",
        choices=["auto", "playwright", "selenium", "scrapy", "requests_httpx", "node_browser", "generic_rpa"],
        help="Collector preset",
    )
    auto_collect.add_argument("--out", required=True, help="Output auto report directory")
    auto_collect.add_argument("--dry-run", action="store_true", help="Write manifest only without copying raw files")
    auto_collect.add_argument("--auto-diagnose", action="store_true", help="Run diagnose and plan after collection")
    auto_collect.add_argument("--auto-handoff", action="store_true", help="Generate Codex/Claude/Cursor handoff after diagnosis")
    auto_collect.add_argument("--auto-sanitize", action="store_true", help="Generate sanitized failure pack")
    auto_collect.add_argument("--open-report", action="store_true", help="Open the first report file when supported")
    auto_collect.add_argument("--broad-scope", action="store_true", help="Allow broad scope folders after explicit user approval")
    watch = sub.add_parser("watch", help="Watch a project folder and create diagnosis packs for new failure evidence")
    watch.add_argument("--project", required=True, help="Authorized project folder to watch")
    watch.add_argument("--out", required=True, help="Output folder for watch reports")
    watch.add_argument(
        "--preset",
        default="auto",
        choices=["auto", "playwright", "selenium", "scrapy", "requests_httpx", "node_browser", "generic_rpa"],
        help="Collector preset",
    )
    watch.add_argument("--auto-diagnose", action="store_true")
    watch.add_argument("--auto-handoff", action="store_true")
    watch.add_argument("--auto-sanitize", action="store_true")
    watch.add_argument("--debounce-seconds", type=float, default=5.0)
    watch.add_argument("--max-events", type=int, default=100)
    watch.add_argument("--once", action="store_true")
    watch.add_argument("--poll-interval", type=float, default=2.0)
    watch.add_argument("--ignore", default="node_modules,.git,.venv,__pycache__")
    adapt = sub.add_parser("adapt", help="Normalize Selenium/Puppeteer/Cypress/Scrapy/requests/httpx logs into a failure pack")
    adapt.add_argument("input", help="Path to a framework failure log folder or file")
    adapt.add_argument("--framework", required=True, choices=sorted(SUPPORTED_FRAMEWORKS), help="Source framework or auto")
    adapt.add_argument("--out", required=True, help="Output failure pack directory")
    pack_logs = sub.add_parser("pack-logs", help="Normalize a raw log folder into a failure pack")
    pack_logs.add_argument("raw_logs", help="Path to a folder containing logs, network summaries, and screenshots")
    pack_logs.add_argument("--out", required=True, help="Output failure pack directory")
    sanitize = sub.add_parser("sanitize", help="Create a redacted shareable failure pack")
    sanitize.add_argument("failed_run", help="Path to a failed run folder or input file")
    sanitize.add_argument("--out", required=True, help="Output shareable failure pack directory")
    run = sub.add_parser("run", help="Run a command and auto-capture a local failure pack")
    run.add_argument("--capture", action="store_true", help="Compatibility flag: capture the wrapped command output")
    run.add_argument("--workspace", default=".failure-doctor", help="Workspace root for captured runs")
    run.add_argument("--run-id", default=None, help="Stable run identifier")
    run.add_argument("--cwd", default=None, help="Working directory for the wrapped command")
    run.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to run after --")
    handoff = sub.add_parser("handoff", help="Generate an AI coding assistant handoff pack from a report")
    handoff.add_argument("report", help="Path to a report directory containing diagnosis.json")
    handoff.add_argument("--target", required=True, choices=["codex", "claude_code", "cursor", "all"], help="Preferred AI coding assistant target")
    handoff.add_argument("--out", required=True, help="Output AI handoff directory")
    patch = sub.add_parser("propose-patch", help="Generate a dry-run patch proposal from a report")
    patch.add_argument("--repo", required=True, help="Repository root to inspect later")
    patch.add_argument("--report", required=True, help="Path to a report directory containing diagnosis.json")
    patch.add_argument("--out", required=True, help="Output patch proposal directory")
    batch = sub.add_parser("batch", help="Diagnose a folder of failed runs and write a fleet-level report")
    batch.add_argument("runs", help="Directory containing failed run folders")
    batch.add_argument("--out", required=True, help="Output batch report directory")
    return parser


def diagnose_inputs(args: argparse.Namespace) -> int:
    _configure_stdio()
    input_path = Path(args.input)
    out_dir = Path(args.out)
    if not input_path.exists():
        print(f"input not found: {input_path}")
        return 1

    evidence = collect_inputs(input_path)
    input_summary = input_summary_for(evidence)
    artifact = build_artifact(evidence, run_id=args.run_id)
    diagnosis = _low_evidence_diagnosis(input_summary) if _is_low_evidence(input_summary) else classify_composite_failure_artifact(artifact)
    public = enrich_for_users(diagnosis, input_summary=input_summary)
    outputs = write_failure_doctor_report(out_dir, artifact, diagnosis, public, evidence, input_summary)

    confidence = float(public.get("confidence", 0.0))
    print("Agent Failure Doctor")
    print(f"Category: {public.get('user_facing_category')} ({confidence:.0%})")
    print(f"Technical: {public.get('technical_category')} / {public.get('subtype', 'n/a')}")
    print(f"Difficulty: {public.get('estimated_fix_difficulty')}")
    print(f"Evidence priority: {', '.join(public.get('evidence_priority', [])) or 'none'}")
    if public.get("missing_evidence"):
        print(f"Missing evidence: {', '.join(public.get('missing_evidence', []))}")
    print(f"Next: {public.get('next_action')}")
    print(f"Report: {out_dir}")
    print(f"Bundle: {outputs['failure_doctor_report.zip']}")
    return 0


def plan_from_report(args: argparse.Namespace) -> int:
    report_dir = Path(args.report)
    out_dir = Path(args.out)
    diagnosis = _load_report_diagnosis(report_dir)
    evidence = _load_optional_json(report_dir / "evidence.json")
    plan = generate_fix_plan(diagnosis, evidence)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "fix_plan.json", plan)
    (out_dir / "fix_plan.md").write_text(render_fix_plan_markdown(plan), encoding="utf-8")
    (out_dir / "codex_fix_prompt.md").write_text(_render_fix_plan_codex_prompt(plan), encoding="utf-8")
    print("Agent Failure Doctor Fix Plan")
    print(f"Root cause: {plan.get('root_cause')}")
    print(f"Risk: {plan.get('risk')}")
    print(f"Output: {out_dir}")
    return 0


def verify_inputs(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    before_diag, before_evidence, before_summary = _diagnose_or_load(Path(args.before), out_dir / "before_report")
    after_diag, after_evidence, after_summary = _diagnose_or_load(Path(args.after), out_dir / "after_report")
    fix_plan = _load_fix_plan(Path(args.fix_plan)) if args.fix_plan else generate_fix_plan(before_diag, before_evidence)
    report = verify_resolution(before_diag, before_evidence, after_diag, after_evidence, fix_plan)
    regression = create_regression_case(str(args.before), str(args.after), report) if args.create_regression or report.get("regression_case_created") else None
    if regression:
        report["regression_case_created"] = True
    write_json(out_dir / "verification_report.json", report)
    (out_dir / "verification_report.md").write_text(render_verification_markdown(report), encoding="utf-8")
    write_json(out_dir / "before_summary.json", before_summary)
    write_json(out_dir / "after_summary.json", after_summary)
    if regression:
        write_json(out_dir / "regression_case.json", regression)
    print("Agent Failure Doctor Verification")
    print(f"Status: {report.get('status')}")
    print(f"Output: {out_dir}")
    return 0


def collect_playwright_inputs(args: argparse.Namespace) -> int:
    summary = collect_playwright_artifacts(Path(args.test_results), Path(args.out))
    print("Agent Failure Doctor Playwright Collector")
    print(f"Output: {args.out}")
    print(f"Evidence priority: {', '.join(summary.get('evidence_priority', [])) or 'none'}")
    return 0


def adapt_framework_inputs(args: argparse.Namespace) -> int:
    try:
        summary = normalize_framework_failure(Path(args.input), str(args.framework), Path(args.out))
    except ValueError as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor Cross-Framework Adapter")
    print(f"Framework: {summary.get('framework')}")
    print(f"Technical: {summary.get('candidate_technical_category')} / {summary.get('subtype')}")
    print(f"Layer: {summary.get('candidate_failure_layer')}")
    print(f"Redaction: {summary.get('redaction_status')}")
    print(f"Output: {args.out}")
    return 0


def pack_log_inputs(args: argparse.Namespace) -> int:
    summary = pack_generic_logs(Path(args.raw_logs), Path(args.out))
    print("Agent Failure Doctor Log Pack")
    print(f"Output: {args.out}")
    print(f"Evidence priority: {', '.join(summary.get('evidence_priority', [])) or 'none'}")
    return 0


def sanitize_inputs(args: argparse.Namespace) -> int:
    try:
        result = sanitize_failure_pack(Path(args.failed_run), Path(args.out))
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    safe = result["safe_to_share"]
    report = result["redaction_report"]
    print("Agent Failure Doctor Sanitize & Share")
    print(f"Output: {result['out_dir']}")
    print(f"Bundle: {result['zip_path']}")
    print(f"Redactions: {report.get('total_redactions', 0)}")
    print(f"Safe to share automatically: {safe.get('safe_to_share')}")
    return 0


def run_command(args: argparse.Namespace) -> int:
    command = list(args.cmd)
    if command and command[0] == "--":
        command = command[1:]
    try:
        result = capture_run(
            command,
            workspace=Path(args.workspace),
            run_id=args.run_id,
            cwd=Path(args.cwd) if args.cwd else None,
        )
    except ValueError as exc:
        print(str(exc))
        return 2

    run_dir = Path(result["run_dir"])
    exit_code = int(result["exit_code"])
    if exit_code != 0:
        diagnose_inputs(argparse.Namespace(input=str(run_dir), out=str(run_dir / "diagnosis"), run_id=result["run_id"]))
        plan_from_report(argparse.Namespace(report=str(run_dir / "diagnosis"), out=str(run_dir / "fix_plan")))
    zip_path = write_shareable_zip(run_dir)
    print("Agent Failure Doctor Auto Capture")
    print(f"Run: {result['run_id']}")
    print(f"Exit code: {exit_code}")
    print(f"Output: {run_dir}")
    print(f"Shareable pack: {zip_path}")
    return exit_code


def handoff_report(args: argparse.Namespace) -> int:
    try:
        result = write_ai_handoff_pack(Path(args.report), Path(args.out), target=str(args.target))
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor AI Handoff")
    print(f"Target: {result['selected_target']}")
    print(f"Output: {result['out_dir']}")
    print(f"Bundle: {result['zip_path']}")
    return 0


def collect_project_inputs(args: argparse.Namespace) -> int:
    try:
        manifest = collect_project(
            Path(args.project),
            Path(args.out),
            preset=str(args.preset),
            dry_run=bool(args.dry_run),
            auto_diagnose=bool(args.auto_diagnose),
            auto_handoff=bool(args.auto_handoff),
            auto_sanitize=bool(args.auto_sanitize),
            open_report=bool(args.open_report),
            broad_scope=bool(args.broad_scope),
        )
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor Auto Collector")
    print(f"Preset: {manifest.get('preset')}")
    print(f"Frameworks: {', '.join(manifest.get('detected_frameworks', []))}")
    print(f"Signals: {', '.join(manifest.get('detected_failure_signals', []))}")
    print(f"Output: {args.out}")
    print(f"Open first: {Path(args.out) / 'open_this_first.md'}")
    return 0


def watch_project_inputs(args: argparse.Namespace) -> int:
    try:
        summary = watch_project(
            Path(args.project),
            Path(args.out),
            preset=str(args.preset),
            auto_diagnose=bool(args.auto_diagnose),
            auto_handoff=bool(args.auto_handoff),
            auto_sanitize=bool(args.auto_sanitize),
            debounce_seconds=float(args.debounce_seconds),
            max_events=int(args.max_events),
            once=bool(args.once),
            poll_interval=float(args.poll_interval),
            ignore=str(args.ignore),
        )
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor Watch")
    print(f"Events seen: {summary.get('events_seen')}")
    print(f"Runs created: {summary.get('runs_created')}")
    print(f"Output: {args.out}")
    return 0


def propose_patch(args: argparse.Namespace) -> int:
    try:
        result = write_patch_proposal(Path(args.repo), Path(args.report), Path(args.out))
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor Patch Proposal")
    print("Mode: proposal only")
    print(f"Output: {result['out_dir']}")
    return 0


def batch_diagnose(args: argparse.Namespace) -> int:
    runs_root = Path(args.runs)
    out_dir = Path(args.out)
    try:
        runs = discover_runs(runs_root)
    except FileNotFoundError as exc:
        print(str(exc))
        return 2
    reports_root = out_dir / "reports"
    summaries: list[dict[str, Any]] = []
    for run_path in runs:
        report_dir = reports_root / run_path.stem
        evidence = collect_inputs(run_path)
        input_summary = input_summary_for(evidence)
        artifact = build_artifact(evidence, run_id=f"batch_{run_path.stem}")
        diagnosis = _low_evidence_diagnosis(input_summary) if _is_low_evidence(input_summary) else classify_composite_failure_artifact(artifact)
        public = enrich_for_users(diagnosis, input_summary=input_summary)
        write_failure_doctor_report(report_dir, artifact, diagnosis, public, evidence, input_summary)
        summaries.append(
            {
                "run_id": run_path.stem,
                "name": run_path.name,
                "source": str(run_path),
                "diagnosis": diagnosis,
                "public": public,
            }
        )
    summary = write_batch_report(out_dir, summaries)
    print("Agent Failure Doctor Batch Diagnosis")
    print(f"Runs: {summary['diagnosed_runs']}/{summary['total_runs']}")
    print(f"Repeated failure groups: {summary['repeated_failures_count']}")
    print(f"Output: {out_dir}")
    return 0


def collect_inputs(path: Path) -> dict[str, Any]:
    files = [path] if path.is_file() else sorted(item for item in path.iterdir() if item.is_file())
    evidence: dict[str, Any] = {
        "source": str(path),
        "trace_zip": None,
        "logs": [],
        "network_events": [],
        "descriptions": [],
        "screenshot_metadata": [],
        "unrecognized_files": [],
    }
    for file_path in files:
        lower = file_path.name.lower()
        if lower.endswith(".zip") and "trace" in lower:
            evidence["trace_zip"] = str(file_path)
        elif lower.endswith(".json") and "network" in lower:
            evidence["network_events"].extend(_read_network_events(file_path))
        elif lower.endswith((".png", ".jpg", ".jpeg")):
            evidence["screenshot_metadata"].append(
                {"name": file_path.name, "size_bytes": file_path.stat().st_size, "image_understanding": "metadata_only"}
            )
        elif lower.endswith(".txt") and ("description" in lower or "user" in lower or "readme" in lower):
            evidence["descriptions"].append({"name": file_path.name, "text": _read_text(file_path)})
        elif lower.endswith((".log", ".txt")):
            evidence["logs"].append({"name": file_path.name, "text": _read_text(file_path)})
        else:
            evidence["unrecognized_files"].append(file_path.name)
    return evidence


def input_summary_for(evidence: Mapping[str, Any]) -> dict[str, Any]:
    observed = {
        "trace_zip": 1 if evidence.get("trace_zip") else 0,
        "logs": len(evidence.get("logs", [])),
        "network_events": len(evidence.get("network_events", [])),
        "descriptions": len(evidence.get("descriptions", [])),
        "screenshots": len(evidence.get("screenshot_metadata", [])),
        "unrecognized_files": len(evidence.get("unrecognized_files", [])),
    }
    priority: list[str] = []
    if observed["trace_zip"]:
        priority.append("trace_zip")
    if observed["logs"]:
        priority.append("log")
    if observed["network_events"]:
        priority.append("network")
    if observed["descriptions"]:
        priority.append("description")
    if observed["screenshots"]:
        priority.append("screenshot_metadata")

    missing: list[str] = []
    if not observed["trace_zip"]:
        missing.append("trace_zip")
    if not observed["logs"]:
        missing.append("error.log")
    if not observed["network_events"]:
        missing.append("network.json")
    if not observed["descriptions"]:
        missing.append("user_description.txt or README.txt")
    if not observed["screenshots"]:
        missing.append("screenshot.png")

    return {
        "source": str(evidence.get("source", "")),
        "observed_evidence": observed,
        "evidence_priority": priority,
        "missing_evidence": missing,
        "recognized_files": _recognized_files(evidence),
        "unrecognized_files": list(evidence.get("unrecognized_files", [])),
        "guidance": _input_guidance(priority, missing),
    }


def build_artifact(evidence: Mapping[str, Any], *, run_id: str | None = None) -> dict[str, Any]:
    trace_zip = evidence.get("trace_zip")
    if trace_zip:
        artifact = artifact_from_playwright_trace(Path(str(trace_zip)), run_id=run_id)
        observations = artifact.setdefault("observations", {})
        if isinstance(observations, dict):
            observations["failure_doctor_inputs"] = _input_summary(evidence)
        return artifact

    log_entries = [item for item in evidence.get("logs", []) if isinstance(item, Mapping)]
    log_text = "\n".join(str(item.get("text", "")) for item in _prioritized_log_entries(log_entries))
    description_text = "\n".join(str(item.get("text", "")) for item in evidence.get("descriptions", []) if isinstance(item, Mapping))
    network_events = evidence.get("network_events", [])
    status_code = _first_status(network_events) or _extract_status_from_text(log_text)
    diagnosis_hint = _diagnosis_hint_from_text(log_text, description_text, network_events)
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": run_id or f"failure_doctor_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "tool": "agent_failure_doctor",
        "target_type": "sanitized_real_failure",
        "summary": "Collected from local AI automation failure inputs",
        "error": {"message": (log_text or description_text)[:500], "stack": "", "status_code": status_code},
        "artifacts": {},
        "observations": {
            "source_adapter": "failure_doctor",
            "log_excerpt": log_text[:1000],
            "user_description": description_text[:1000],
            "network_events": network_events[:20],
            "missing_selectors": diagnosis_hint.get("missing_selectors", []),
            "screenshot_metadata": evidence.get("screenshot_metadata", []),
            **diagnosis_hint,
        },
        "expected": {"required_fields": diagnosis_hint.get("expected_fields", [])},
        "actual": {"fields": diagnosis_hint.get("actual_fields", {}), "array_length": diagnosis_hint.get("array_length")},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {
            "sanitized": True,
            "contains_credentials": False,
            "external_network_required": False,
            "user_authorized_or_synthetic": True,
            "redaction_notes": "Generated from local user-provided failure inputs; review before sharing.",
        },
    }


def _prioritized_log_entries(entries: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    def priority(entry: Mapping[str, Any]) -> tuple[int, str]:
        name = str(entry.get("name") or "").lower()
        if name in {"error.log", "stderr.log"}:
            return (0, name)
        if "error" in name or "stderr" in name:
            return (1, name)
        if name.endswith(".log"):
            return (2, name)
        if "console" in name or "stdout" in name:
            return (4, name)
        return (3, name)

    return sorted(entries, key=priority)


def enrich_for_users(diagnosis: Mapping[str, Any], input_summary: Mapping[str, Any] | None = None) -> dict[str, Any]:
    technical = str(diagnosis.get("failure_type", "unknown"))
    subtype = str(diagnosis.get("subtype", ""))
    category = user_category_for(technical, subtype)
    input_summary = input_summary or {}
    return {
        "user_facing_category": category,
        "technical_category": technical,
        "subtype": diagnosis.get("subtype"),
        "failure_layer": failure_layer_for(technical),
        "safe_next_action": True,
        "confidence": diagnosis.get("confidence", 0.0),
        "confidence_reason": confidence_reason_for(diagnosis),
        "estimated_fix_difficulty": estimated_fix_difficulty_for(technical, subtype),
        "evidence_level": diagnosis.get("evidence_level", "inferred"),
        "evidence": diagnosis.get("evidence", []),
        "suggested_fix": diagnosis.get("suggested_fix", []),
        "missing_evidence": list(input_summary.get("missing_evidence", [])),
        "evidence_priority": list(input_summary.get("evidence_priority", [])),
        "next_action": NEXT_ACTION,
    }


def user_category_for(technical: str, subtype: str = "") -> str:
    if technical == "website_change":
        return "网站结构变化"
    if technical == "anti_bot_risk":
        return "疑似风控/访问限制"
    if technical in {"auth_expiry", "playwright_storage_state_context"}:
        return "登录状态失效"
    if technical in {"selector_drift", "playwright_shadow_dom_locator", "playwright_strict_mode_violation", "playwright_frame_locator", "selector_syntax_error"}:
        return "按钮/元素找不到"
    if technical in {"popup_or_overlay_blocking", "popup_or_new_page"}:
        return "弹窗/遮罩挡住"
    if technical in {"browser_driver_mismatch", "target_closed_or_page_crash", "cdp_protocol_error", "environment_config_mismatch"}:
        return "浏览器环境不一致"
    if technical in {"navigation_or_wait_timeout", "browser_context_or_origin_policy", "viewport_responsive_layout_mismatch", "async_hydration_timing", "playwright_execution_context_destroyed"}:
        return "页面没加载完"
    if technical in {"playwright_popup"}:
        return "弹窗/遮罩挡住"
    if technical in {"response_shape_change", "fixture_or_mock_missing"} or (technical == "playwright_route_mock_har" and subtype == "mock_response_shape_mismatch"):
        return "接口返回变了"
    if technical == "rate_limit_or_soft_block":
        return "请求被限流"
    if technical == "network_http_error":
        return "网络/代理问题"
    if technical in {"runtime_api_missing", "toolchain_environment", "playwright_browser_context_closed", "cdp_websocket_disconnected"}:
        return "浏览器环境不一致"
    if technical in {"playwright_file_chooser", "playwright_download", "download_not_saved"}:
        return "文件上传下载失败"
    if technical == "insufficient_evidence":
        return "证据不足"
    return "代码等待逻辑错误"


def failure_layer_for(technical: str) -> str:
    if technical == "website_change":
        return "website_change"
    if technical == "anti_bot_risk":
        return "anti_bot_risk"
    if technical == "insufficient_evidence":
        return "insufficient_evidence"
    if technical in {
        "network_http_error",
        "toolchain_environment",
        "runtime_api_missing",
        "playwright_browser_context_closed",
        "cdp_websocket_disconnected",
        "browser_driver_mismatch",
        "target_closed_or_page_crash",
        "cdp_protocol_error",
        "environment_config_mismatch",
    }:
        return "environment"
    return "automation_engineering"


def estimated_fix_difficulty_for(technical: str, subtype: str = "") -> str:
    if technical == "anti_bot_risk":
        return "hard"
    if technical == "website_change":
        return "medium"
    easy = {
        "selector_drift",
        "playwright_strict_mode_violation",
        "playwright_frame_locator",
        "playwright_file_chooser",
        "playwright_download",
    }
    hard = {
        "cdp_websocket_disconnected",
        "toolchain_environment",
        "runtime_api_missing",
        "agent_repetition_loop",
        "playwright_browser_context_closed",
    }
    if technical in easy:
        return "easy"
    if technical in hard:
        return "hard"
    return "medium"


def confidence_reason_for(diagnosis: Mapping[str, Any]) -> str:
    technical = diagnosis.get("failure_type", "unknown")
    subtype = diagnosis.get("subtype", "n/a")
    confidence = diagnosis.get("confidence", 0.0)
    evidence_level = diagnosis.get("evidence_level", "inferred")
    evidence = diagnosis.get("evidence", [])
    first_evidence = str(evidence[0]) if isinstance(evidence, list) and evidence else "no direct evidence item"
    return (
        f"confidence={confidence}, evidence_level={evidence_level}; "
        f"classified as {technical}/{subtype} because evidence includes: {first_evidence}. "
        "为什么不是其他分类: the current evidence first matches category-specific log, trace, or adapter markers; other categories remain alternatives only."
    )


def write_failure_doctor_report(
    out_dir: Path,
    artifact: Mapping[str, Any],
    diagnosis: Mapping[str, Any],
    public: Mapping[str, Any],
    evidence: Mapping[str, Any],
    input_summary: Mapping[str, Any],
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "diagnosis.json": out_dir / "diagnosis.json",
        "diagnosis.md": out_dir / "diagnosis.md",
        "evidence.json": out_dir / "evidence.json",
        "input_summary.json": out_dir / "input_summary.json",
        "repair_suggestions.md": out_dir / "repair_suggestions.md",
        "issue_draft.md": out_dir / "issue_draft.md",
        "codex_fix_prompt.md": out_dir / "codex_fix_prompt.md",
        "failure_doctor_report.zip": out_dir / "failure_doctor_report.zip",
    }
    composite_payload = _composite_public_fields(diagnosis)
    diagnosis_payload = {**dict(public), **composite_payload, "raw_diagnosis": dict(diagnosis)}
    outputs["diagnosis.json"].write_text(_json(diagnosis_payload), encoding="utf-8")
    outputs["diagnosis.md"].write_text(_render_public_markdown(public, diagnosis, artifact, input_summary), encoding="utf-8")
    outputs["evidence.json"].write_text(_json({"inputs": evidence, "artifact": artifact, "diagnosis": diagnosis_payload}), encoding="utf-8")
    outputs["input_summary.json"].write_text(_json(input_summary), encoding="utf-8")
    outputs["repair_suggestions.md"].write_text(_render_repair_suggestions(diagnosis), encoding="utf-8")
    outputs["issue_draft.md"].write_text(render_issue_draft(artifact, diagnosis, _doctor_summary(diagnosis)), encoding="utf-8")
    outputs["codex_fix_prompt.md"].write_text(_render_codex_fix_prompt(public, diagnosis), encoding="utf-8")
    _write_report_zip(out_dir, outputs["failure_doctor_report.zip"])
    return outputs


def _diagnosis_hint_from_text(log_text: str, description_text: str, network_events: Any) -> dict[str, Any]:
    text = f"{log_text}\n{description_text}".lower()
    hints: dict[str, Any] = {}
    adapter_hint = _adapter_hint_from_text(log_text)
    if adapter_hint:
        hints["adapter_failure_hint"] = adapter_hint
    if "err_proxy_connection_failed" in text or "proxy_connection_failed" in text:
        hints.update({"network_error": "proxy connection failed", "transport_marker": "proxy", "subtype_hint": "proxy_connection_failed"})
    if "err_name_not_resolved" in text:
        hints.update({"network_error": "dns name not resolved", "transport_marker": "dns", "subtype_hint": "dns_name_not_resolved"})
    if "err_cert_authority_invalid" in text or "err_cert" in text or "certificate" in text:
        hints.update({"network_error": "tls certificate error", "transport_marker": "tls", "subtype_hint": "tls_certificate_error"})
    if "strict mode violation" in text:
        hints["strict_mode_violation"] = True
    if "timeout waiting for selector" in text or "locator.click" in text:
        hints["missing_selectors"] = ["button.submit" if "button.submit" in text else "unknown"]
    if "page.goto" in text and "timeout" in text:
        hints["navigation_timeout"] = True
    if "page stayed" in text or "never worked" in text:
        hints["wait_or_click_failed"] = True
    if "storage_state expected" in text or "storagestate expected" in text or "storage state expected" in text:
        hints["storage_state_expected"] = True
        if "not loaded" in text or "missing_cookie" in text or "missing session cookie" in text:
            hints["storage_state_loaded"] = False
    statuses = [item.get("status") for item in network_events if isinstance(item, Mapping)]
    if 429 in statuses or "429" in text:
        hints["rate_limit_marker"] = True
    return hints


def _adapter_hint_from_text(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    marker_map = {
        "framework": "AFD_FRAMEWORK=",
        "technical_category": "AFD_TECHNICAL_CATEGORY=",
        "subtype": "AFD_SUBTYPE=",
        "failure_layer": "AFD_FAILURE_LAYER=",
        "error_family": "AFD_ERROR_FAMILY=",
    }
    for raw_line in text.splitlines():
        line = raw_line.strip()
        for key, marker in marker_map.items():
            if line.startswith(marker):
                fields[key] = line[len(marker) :].strip()
    return fields


def _render_public_markdown(
    public: Mapping[str, Any],
    diagnosis: Mapping[str, Any],
    artifact: Mapping[str, Any],
    input_summary: Mapping[str, Any],
) -> str:
    evidence = "\n".join(f"- {item}" for item in public.get("evidence", [])) or "- No direct evidence yet; collect trace, logs, or network evidence."
    fixes = "\n".join(f"- {item}" for item in public.get("suggested_fix", [])) or "- Collect a minimal reproduction before editing code."
    missing = "\n".join(f"- {item}" for item in public.get("missing_evidence", [])) or "- No obvious missing evidence."
    priority = ", ".join(public.get("evidence_priority", [])) or "none"
    composite = _render_composite_markdown(diagnosis)
    return "\n".join(
        [
            "# Agent Failure Diagnosis",
            "",
            "## 结论",
            "",
            f"This failure most likely belongs to **{public.get('user_facing_category')}**.",
            f"- Technical category: `{public.get('technical_category')}`",
            f"- Subtype: `{public.get('subtype', 'n/a')}`",
            f"- Confidence: `{public.get('confidence', 0)}`",
            f"- Fix difficulty: `{public.get('estimated_fix_difficulty')}`",
            f"- Evidence priority: `{priority}`",
            "",
            "## 证据",
            "",
            evidence,
            "",
            "## Input Summary",
            "",
            f"- Evidence priority: `{priority}`",
            "- Missing evidence:",
            missing,
            "- Details: `input_summary.json`",
            "",
            "## 为什么",
            "",
            str(public.get("confidence_reason")),
            "",
            "## 下一步",
            "",
            fixes,
            f"- {public.get('next_action')}",
            "",
            "## 给 Codex 的修复指令",
            "",
            "Give `codex_fix_prompt.md` to Codex or Claude. It contains conservative repair steps, recommended repair steps, verification commands, and forbidden edit boundaries.",
            "",
            "## Technical Details",
            "",
            composite,
            "",
            render_markdown_report(diagnosis, artifact),
        ]
    )


def _composite_public_fields(diagnosis: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "schema_version",
        "diagnosis_mode",
        "primary_failure",
        "secondary_failures",
        "blocking_failure",
        "downstream_failures",
        "competing_hypotheses",
        "evidence_graph",
        "repair_order",
        "why_this_order",
        "score_breakdown",
        "why_not_other_categories",
    )
    return {key: diagnosis[key] for key in keys if key in diagnosis}


def _render_composite_markdown(diagnosis: Mapping[str, Any]) -> str:
    if "primary_failure" not in diagnosis:
        return "## Composite Diagnosis\n\nComposite diagnosis was not generated for this report."
    primary = diagnosis.get("primary_failure", {})
    secondary = diagnosis.get("secondary_failures", [])
    blocking = diagnosis.get("blocking_failure", {})
    repair_order = diagnosis.get("repair_order", [])
    graph = diagnosis.get("evidence_graph", {})
    return "\n".join(
        [
            "## Composite Diagnosis",
            "",
            "### Primary Failure",
            "",
            f"- `{primary.get('technical_category')}` / `{primary.get('subtype')}`",
            "",
            "### Secondary Failures",
            "",
            _bullets([f"{item.get('technical_category')} ({item.get('relationship_to_primary')})" for item in secondary]) or "- none",
            "",
            "### Blocking Failure",
            "",
            f"- `{blocking.get('technical_category')}`: {blocking.get('reason')}",
            "",
            "### Evidence Graph Summary",
            "",
            f"- Nodes: `{len(graph.get('nodes', [])) if isinstance(graph, Mapping) else 0}`",
            f"- Edges: `{len(graph.get('edges', [])) if isinstance(graph, Mapping) else 0}`",
            "",
            "### Repair Order",
            "",
            _bullets(repair_order) or "- collect more evidence",
        ]
    )


def _bullets(items: Any) -> str:
    if not isinstance(items, list):
        return ""
    return "\n".join(f"- {item}" for item in items)


def _render_codex_fix_prompt(public: Mapping[str, Any], diagnosis: Mapping[str, Any]) -> str:
    if public.get("technical_category") == "anti_bot_risk":
        return _render_anti_bot_codex_fix_prompt(public, diagnosis)
    if public.get("technical_category") == "website_change":
        return _render_website_change_codex_fix_prompt(public, diagnosis)

    evidence = "\n".join(f"- {item}" for item in diagnosis.get("evidence", [])) or "- Evidence is thin; collect logs, trace, or network data first."
    fixes = list(diagnosis.get("suggested_fix", [])) if isinstance(diagnosis.get("suggested_fix", []), list) else []
    conservative = fixes[0] if fixes else "Collect a minimal reproduction and do not guess the root cause."
    recommended = "\n".join(f"- {item}" for item in fixes[1:]) or "- Make the smallest code change that addresses the diagnosed cause, then add a regression test."
    missing = "\n".join(f"- {item}" for item in public.get("missing_evidence", [])) or "- Current evidence is sufficient for an initial fix plan."
    verification_commands = "\n".join(
        [
            "- Run the affected test or minimal reproduction.",
            "- For this repo, run: `python -m unittest discover -s tests -p \"test_*.py\"`.",
            "- If it still fails, save fresh trace/screenshot/log evidence and regenerate the diagnosis report.",
        ]
    )
    return f"""# Codex Fix Prompt

请修复这个 AI 自动化失败。

## Diagnosis

- User-facing category: {public.get("user_facing_category")}
- Technical category: {public.get("technical_category")}
- Subtype: {public.get("subtype", "n/a")}
- Confidence: {public.get("confidence", 0)}
- Fix difficulty: {public.get("estimated_fix_difficulty")}
- Confidence reason: {public.get("confidence_reason")}

## Evidence

{evidence}

## Missing Evidence

{missing}

## 保守修复

- {conservative}

## 推荐修复

{recommended}

## 验证命令

{verification_commands}

## 禁止修改范围

1. 不要改业务逻辑。
2. 不要加入 Cookie、Token、Authorization 或密码。
3. 不要加入 challenge solving、access-control defeat 或 bot-evasion logic。
4. 不要提交敏感截图、trace 或日志。
5. 不要把网络、代理或环境问题误修成 selector 改动。
"""


def _render_website_change_codex_fix_prompt(public: Mapping[str, Any], diagnosis: Mapping[str, Any]) -> str:
    evidence = "\n".join(f"- {item}" for item in diagnosis.get("evidence", [])) or "- Need fresh DOM/network evidence."
    fixes = "\n".join(f"- {item}" for item in diagnosis.get("suggested_fix", [])) or "- Update the automation contract from fresh evidence."
    return f"""# Codex Fix Prompt

Please fix this browser automation failure.

Diagnosis:
- Layer: website_change
- Category: {public.get("user_facing_category")}
- Technical reason: {public.get("technical_category")}
- Subtype: {public.get("subtype")}
- Confidence: {public.get("confidence")}

Evidence:
{evidence}

Required changes:
{fixes}
- Use the new DOM snapshot or network.json to update selectors, endpoints, JSON paths, pagination, login flow, or download flow.
- Add a regression test for the new site contract.

Verification:
- Run the affected automation test or minimal reproduction.
- Re-run Agent Failure Doctor with fresh sanitized evidence if it still fails.

Do not change:
- Do not add challenge-defeat, access-control defeat, credential collection, or sensitive artifact storage.
- Do not treat suspected access-control risk as a normal selector update.
"""


def _render_anti_bot_codex_fix_prompt(public: Mapping[str, Any], diagnosis: Mapping[str, Any]) -> str:
    evidence = "\n".join(f"- {item}" for item in diagnosis.get("evidence", [])) or "- Access-control risk evidence is thin."
    return f"""# Codex Fix Prompt

Please triage this automation failure conservatively.

Diagnosis:
- Layer: anti_bot_risk
- Category: {public.get("user_facing_category")}
- Technical reason: {public.get("technical_category")}
- Subtype: {public.get("subtype")}
- Confidence: {public.get("confidence")}

Evidence:
{evidence}

Safe next action:
- Do not keep blindly changing selectors.
- Confirm authorization before continuing.
- Check whether an official API, authorized export, manual review, or platform-owner contact path exists.
- Reduce request volume where appropriate.
- Stop the automation if authorization or platform terms are unclear.

Verification:
- Save a sanitized trace/log/network summary.
- Confirm whether the same failure appears with an authorized/manual flow.

Forbidden scope:
- Do not implement challenge defeat, access-control defeat, credential extraction, account rotation, network rotation, or automated challenge solving.
"""


def _load_report_diagnosis(report_dir: Path) -> dict[str, Any]:
    path = report_dir / "diagnosis.json"
    if not path.exists():
        raise SystemExit(f"diagnosis.json not found in report directory: {report_dir}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("raw_diagnosis")
    if isinstance(raw, Mapping):
        merged = dict(raw)
        merged.setdefault("technical_category", payload.get("technical_category"))
        merged.setdefault("failure_layer", payload.get("failure_layer"))
        merged.setdefault("subtype", payload.get("subtype"))
        return merged
    return payload


def _load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_fix_plan(path: Path) -> dict[str, Any]:
    if path.is_dir():
        path = path / "fix_plan.json"
    if not path.exists():
        raise SystemExit(f"fix_plan.json not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _diagnose_or_load(path: Path, scratch_report_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if path.is_dir() and (path / "diagnosis.json").exists():
        diagnosis = _load_report_diagnosis(path)
        evidence = _load_optional_json(path / "evidence.json")
        summary = _load_optional_json(path / "input_summary.json")
        return diagnosis, evidence, summary

    evidence_inputs = collect_inputs(path)
    summary = input_summary_for(evidence_inputs)
    artifact = build_artifact(evidence_inputs, run_id=f"verify_{path.name}")
    diagnosis = _low_evidence_diagnosis(summary) if _is_low_evidence(summary) else diagnose_artifact(artifact)
    return diagnosis, {"inputs": evidence_inputs, "artifact": artifact, "diagnosis": diagnosis}, summary


def _render_fix_plan_codex_prompt(plan: Mapping[str, Any]) -> str:
    areas = "\n".join(f"- {item}" for item in plan.get("recommended_change_area", []))
    return "\n".join(
        [
            "# Codex Fix Prompt",
            "",
            "Please implement the failure fix described by this plan.",
            "",
            f"- Root cause: {plan.get('root_cause')}",
            f"- Fix intent: {plan.get('fix_intent')}",
            f"- Risk: {plan.get('risk')}",
            "",
            "## Recommended Change Area",
            "",
            areas,
            "",
            "## Verification",
            "",
            str(plan.get("verification_strategy")),
            "",
            "## Boundaries",
            "",
            "- Do not change unrelated business logic.",
            "- Do not add access-control defeat logic, challenge automation, credential extraction, or unauthorized collection.",
            "- After editing, rerun the failing automation and save after-run evidence for `failure-doctor verify`.",
        ]
    )


def _low_evidence_diagnosis(input_summary: Mapping[str, Any]) -> dict[str, Any]:
    missing = ", ".join(input_summary.get("missing_evidence", []))
    return {
        "failure_type": "insufficient_evidence",
        "subtype": "needs_trace_or_log",
        "confidence": 0.2,
        "evidence_level": "low",
        "evidence": ["only low-priority evidence was provided"],
        "suggested_fix": [
            f"需要补充这些材料: {missing}",
            "prefer trace.zip or error.log first; add network.json when the failure involves HTTP/API behavior",
        ],
        "can_auto_fix": False,
        "synthetic_only": True,
    }


def _is_low_evidence(input_summary: Mapping[str, Any]) -> bool:
    observed = input_summary.get("observed_evidence", {})
    if not isinstance(observed, Mapping):
        return True
    return not observed.get("trace_zip") and not observed.get("logs") and not observed.get("network_events")


def _doctor_summary(diagnosis: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ready": True,
        "checks": [{"name": "failure_doctor", "status": "pass", "detail": "local multi-input diagnosis generated"}],
        "errors": [],
        "next_steps": ["review codex_fix_prompt.md before giving it to a coding assistant"],
        "diagnosis": dict(diagnosis),
    }


def _recognized_files(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "trace_zip": evidence.get("trace_zip"),
        "logs": [item.get("name") for item in evidence.get("logs", []) if isinstance(item, Mapping)],
        "network_events": len(evidence.get("network_events", [])),
        "descriptions": [item.get("name") for item in evidence.get("descriptions", []) if isinstance(item, Mapping)],
        "screenshots": [item.get("name") for item in evidence.get("screenshot_metadata", []) if isinstance(item, Mapping)],
    }


def _input_guidance(priority: list[str], missing: list[str]) -> str:
    if not priority:
        return "No diagnosable material was recognized; provide at least trace.zip or error.log."
    if priority == ["screenshot_metadata"] or priority == ["description"] or set(priority).issubset({"description", "screenshot_metadata"}):
        return "Evidence is weak; this run only supports low-confidence triage until trace.zip, error.log, or network.json is provided."
    if "trace_zip" in priority:
        return "trace.zip was recognized and will be used as the strongest evidence source."
    return "Logs or network evidence were recognized; add trace.zip to improve evidence quality when available."


def _read_network_events(path: Path) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []


def _first_status(events: Any) -> int | None:
    if not isinstance(events, list):
        return None
    for event in events:
        if isinstance(event, Mapping):
            status = event.get("status") or event.get("status_code")
            try:
                return int(status)
            except (TypeError, ValueError):
                continue
    return None


def _extract_status_from_text(text: str) -> int | None:
    for status in (401, 403, 429, 500, 502, 503):
        if str(status) in text:
            return status
    return None


def _input_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "trace_zip": evidence.get("trace_zip"),
        "log_count": len(evidence.get("logs", [])),
        "network_event_count": len(evidence.get("network_events", [])),
        "description_count": len(evidence.get("descriptions", [])),
        "screenshot_count": len(evidence.get("screenshot_metadata", [])),
    }


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")[:5000]


def _write_report_zip(root: Path, zip_path: Path) -> None:
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(root.iterdir()):
            if path == zip_path or not path.is_file():
                continue
            archive.write(path, path.name)


def _json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
