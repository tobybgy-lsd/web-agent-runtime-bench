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
from failure_doctor.agent_invocation import AGENT_TARGETS, bootstrap_agent_frontend
from failure_doctor.auto_collect import collect_project, watch_project
from failure_doctor.run_capture import capture_run, write_shareable_zip
from failure_doctor.sanitize_share import sanitize_failure_pack
from failure_doctor.safety.evaluator import evaluate_safety
from failure_doctor.ocr_evidence.cli import handle_ocr_evidence
from failure_doctor.ocr_evidence.extractor import extract_ocr_evidence
from failure_doctor.full_chain import write_full_chain_report
from failure_doctor.regulated_industry import write_regulated_eval_report
from failure_doctor.regulated_industry.evaluator import SUPPORTED_SUITES
from failure_doctor.visual_runtime.adapter import adapt_visual_artifacts
from failure_doctor.visual_runtime.compare import compare_visual_runs
from failure_doctor.visual_runtime.loader import load_visual_run, validate_visual_run
from failure_doctor.visual_runtime.profiler import profile_visual_run
from failure_doctor.visual_runtime.report import write_visual_runtime_report
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
from tools.failure_artifacts.visual_failure_doctor import diagnose_visual_failure
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
    if args.command == "agent-bootstrap":
        return agent_bootstrap(args)
    if args.command == "propose-patch":
        return propose_patch(args)
    if args.command == "batch":
        return batch_diagnose(args)
    if args.command == "visual-diagnose":
        return visual_diagnose_inputs(args)
    if args.command == "visual-runtime":
        return visual_runtime_inputs(args)
    if args.command == "ocr-evidence":
        return handle_ocr_evidence(args)
    if args.command == "safety-evaluate":
        return safety_evaluate_inputs(args)
    if args.command == "regulated-eval":
        return regulated_eval_inputs(args)
    if args.command == "full-chain-eval":
        return full_chain_eval_inputs(args)
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
    auto_collect.add_argument("--safety-evaluate", action="store_true", help="Run local safety and compliance evaluation after collection")
    auto_collect.add_argument("--open-report", action="store_true", help="Open the first report file when supported")
    auto_collect.add_argument("--broad-scope", action="store_true", help="Allow broad scope folders after explicit user approval")
    safety = sub.add_parser("safety-evaluate", help="Evaluate local artifacts for safety, shareability, and compliance risks")
    safety_inputs = safety.add_mutually_exclusive_group(required=True)
    safety_inputs.add_argument("--project", help="Authorized project folder to evaluate")
    safety_inputs.add_argument("--report", help="Failure Doctor report directory to evaluate")
    safety_inputs.add_argument("--failure-pack", help="Failure pack directory to evaluate")
    safety_inputs.add_argument("--ai-handoff", help="AI handoff directory to evaluate without executing it")
    safety_inputs.add_argument("--patch-proposal", help="Patch proposal directory to evaluate without applying it")
    safety_inputs.add_argument("--cloud-artifact", help="Offline cloud browser artifact directory to evaluate")
    safety.add_argument("--out", required=True, help="Output safety report directory")
    safety.add_argument("--allow-broad-scope", action="store_true", help="Allow broad project scope, while still blocking sensitive paths")
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
    agent_bootstrap_cmd = sub.add_parser("agent-bootstrap", help="Generate frontend invocation instructions for AI coding agents")
    agent_bootstrap_cmd.add_argument("--target", required=True, choices=sorted((*AGENT_TARGETS, "all")), help="Agent frontend target")
    agent_bootstrap_cmd.add_argument("--project", required=True, help="Authorized project folder")
    patch = sub.add_parser("propose-patch", help="Generate a dry-run patch proposal from a report")
    patch.add_argument("--repo", required=True, help="Repository root to inspect later")
    patch.add_argument("--report", required=True, help="Path to a report directory containing diagnosis.json")
    patch.add_argument("--out", required=True, help="Output patch proposal directory")
    batch = sub.add_parser("batch", help="Diagnose a folder of failed runs and write a fleet-level report")
    batch.add_argument("runs", help="Directory containing failed run folders")
    batch.add_argument("--out", required=True, help="Output batch report directory")
    visual = sub.add_parser("visual-diagnose", help="Diagnose visual/screenshot/DOM-based failures from evidence directory")
    visual.add_argument("input", help="Directory containing screenshot.png, dom_snapshot.html, click_coordinates.json, ocr_excerpt.txt")
    visual.add_argument("--out", required=True, help="Output visual diagnosis report directory")
    visual.add_argument("--ocr-provider", default=None, choices=["mock_ocr", "paddleocr_local", "paddleocr_vl_local", "baidu_cloud_ocr", "baidu_cloud_doc_parser", "external_json_import"], help="Optional OCR evidence provider")
    visual_runtime = sub.add_parser("visual-runtime", help="Offline observability for screenshot-driven visual agent runtimes")
    visual_runtime_sub = visual_runtime.add_subparsers(dest="visual_runtime_command", required=True)
    visual_diag = visual_runtime_sub.add_parser("diagnose", help="Diagnose an offline visual runtime artifact")
    visual_diag.add_argument("--input", required=True, help="visual_run directory")
    visual_diag.add_argument("--out", required=True, help="Output visual report directory")
    visual_diag.add_argument("--mock-vlm", action="store_true", help="Use deterministic local mock VLM responses when present")
    visual_diag.add_argument("--no-dom", action="store_true", help="Do not require or inspect DOM snapshots")
    visual_diag.add_argument("--dom-optional", action="store_true", help="Use DOM snapshots when present, otherwise degrade to pure visual")
    visual_diag.add_argument("--redact-images", action="store_true", help="Reserved for adapters; diagnosis never uploads images")
    visual_diag.add_argument("--safety-evaluate", action="store_true", help="Evaluate shareability and block sensitive visual artifacts")
    visual_diag.add_argument("--ocr-provider", default=None, choices=["mock_ocr", "paddleocr_local", "paddleocr_vl_local", "external_json_import"], help="Optional local OCR evidence provider")
    visual_profile = visual_runtime_sub.add_parser("profile", help="Profile an offline visual runtime artifact")
    visual_profile.add_argument("--input", required=True)
    visual_profile.add_argument("--out", required=True)
    visual_profile.add_argument("--no-dom", action="store_true")
    visual_profile.add_argument("--dom-optional", action="store_true")
    visual_compare = visual_runtime_sub.add_parser("compare", help="Compare two offline visual runtime artifacts")
    visual_compare.add_argument("--baseline", required=True)
    visual_compare.add_argument("--candidate", required=True)
    visual_compare.add_argument("--out", required=True)
    visual_adapt = visual_runtime_sub.add_parser("adapt", help="Normalize offline visual-agent artifacts into visual_run format")
    visual_adapt.add_argument("--source", required=True, choices=["skyvern", "skyvern_mock", "claude_computer_use", "claude_computer_use_mock", "generic", "generic_screenshot_agent", "playwright_screenshot", "cursor_agent", "codex_agent"])
    visual_adapt.add_argument("--input", required=True)
    visual_adapt.add_argument("--out", required=True)
    visual_adapt.add_argument("--redact-images", action="store_true")
    visual_validate = visual_runtime_sub.add_parser("validate", help="Validate visual_run schema and safety counters")
    visual_validate.add_argument("--input", required=True)
    visual_validate.add_argument("--out", required=True)
    visual_validate.add_argument("--no-dom", action="store_true")
    visual_validate.add_argument("--dom-optional", action="store_true")
    ocr = sub.add_parser("ocr-evidence", help="Extract and compare local OCR/document evidence")
    ocr_sub = ocr.add_subparsers(dest="ocr_command", required=True)
    ocr_extract = ocr_sub.add_parser("extract", help="Extract local OCR/document evidence")
    ocr_extract.add_argument("--input", required=True, help="Input image/PDF/folder or mock OCR fixture directory")
    ocr_extract.add_argument("--out", required=True, help="Output OCR report directory")
    ocr_extract.add_argument("--provider", default="mock_ocr", choices=["mock_ocr", "paddleocr_local", "paddleocr_vl_local", "baidu_cloud_ocr", "baidu_cloud_doc_parser", "external_json_import"])
    ocr_extract.add_argument("--model-dir", default=None, help="Local model directory for optional local OCR providers")
    ocr_extract.add_argument("--allow-cloud-ocr", action="store_true", help="Explicitly allow cloud OCR after safety evaluation")
    ocr_extract.add_argument("--no-cloud", action="store_true", help="Block all cloud OCR providers")
    ocr_extract.add_argument("--redact-before-cloud", action="store_true", help="Require redaction before any cloud OCR attempt")
    ocr_extract.add_argument("--safety-evaluate", action="store_true", help="Evaluate local safety before provider use")
    ocr_extract.add_argument("--max-file-mb", type=int, default=50)
    ocr_extract.add_argument("--max-total-mb", type=int, default=500)
    ocr_extract.add_argument("--document-mode", default="mixed", choices=["image", "pdf", "table", "form", "mixed"])
    ocr_compare = ocr_sub.add_parser("compare", help="Compare OCR evidence with DOM text")
    ocr_compare.add_argument("--ocr", required=True, help="OCR report directory")
    ocr_compare.add_argument("--dom", required=True, help="DOM snapshot HTML")
    ocr_compare.add_argument("--out", required=True, help="Output comparison report directory")
    ocr_compare_vlm = ocr_sub.add_parser("compare-vlm", help="Compare OCR evidence with offline VLM responses")
    ocr_compare_vlm.add_argument("--ocr", required=True, help="OCR report directory")
    ocr_compare_vlm.add_argument("--vlm", required=True, help="Offline vlm_responses.jsonl")
    ocr_compare_vlm.add_argument("--out", required=True, help="Output comparison report directory")
    ocr_validate = ocr_sub.add_parser("validate", help="Validate OCR evidence report")
    ocr_validate.add_argument("--input", required=True, help="OCR report directory")
    ocr_validate.add_argument("--out", required=True, help="Output validation report directory")
    regulated = sub.add_parser("regulated-eval", help="Run local-only regulated industry mock workflow evaluation")
    regulated.add_argument("--suite", required=True, choices=SUPPORTED_SUITES, help="Synthetic regulated suite")
    regulated.add_argument("--case", default=None, help="Optional case id or subtype")
    regulated.add_argument("--out", required=True, help="Output regulated evaluation report directory")
    full_chain = sub.add_parser("full-chain-eval", help="Evaluate the full local agent failure workflow chain")
    input_group = full_chain.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", help="Failed run, report, or local artifact directory")
    input_group.add_argument("--batch", help="Directory containing multiple failed run folders")
    full_chain.add_argument("--out", required=True, help="Output full-chain evaluation directory")
    full_chain.add_argument("--include-safety", action="store_true")
    full_chain.add_argument("--include-ocr", action="store_true")
    full_chain.add_argument("--include-visual", action="store_true")
    full_chain.add_argument("--include-regulated", action="store_true")
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


def agent_bootstrap(args: argparse.Namespace) -> int:
    try:
        manifest = bootstrap_agent_frontend(Path(args.project), target=str(args.target))
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor Frontend Invocation Pack")
    print(f"Targets: {', '.join(manifest.get('targets', []))}")
    print(f"Entrypoint: {manifest.get('entrypoint')}")
    print(f"Agents root: {manifest.get('agents_root')}")
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
        if bool(getattr(args, "safety_evaluate", False)):
            safety_report = evaluate_safety(
                report=Path(args.out),
                out_dir=Path(args.out) / "safety_report",
                allow_broad_scope=bool(args.broad_scope),
            )
            _append_safety_summary(Path(args.out) / "open_this_first.md", safety_report)
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


def safety_evaluate_inputs(args: argparse.Namespace) -> int:
    try:
        report = evaluate_safety(
            project=Path(args.project) if args.project else None,
            report=Path(args.report) if args.report else None,
            failure_pack=Path(args.failure_pack) if args.failure_pack else None,
            ai_handoff=Path(args.ai_handoff) if args.ai_handoff else None,
            patch_proposal=Path(args.patch_proposal) if args.patch_proposal else None,
            cloud_artifact=Path(args.cloud_artifact) if args.cloud_artifact else None,
            out_dir=Path(args.out),
            allow_broad_scope=bool(args.allow_broad_scope),
        )
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor Safety Evaluation")
    print(f"Status: {report.get('overall_status')}")
    print(f"Risk: {report.get('risk_level')}")
    print(f"Shareability: {report.get('shareability', {}).get('decision')}")
    print(f"Output: {args.out}")
    return 0 if report.get("overall_status") != "blocked" else 3


def _append_safety_summary(open_first: Path, report: Mapping[str, Any]) -> None:
    summary = "\n".join(
        [
            "",
            "## Safety evaluation",
            "",
            f"- Status: `{report.get('overall_status')}`",
            f"- Risk level: `{report.get('risk_level')}`",
            f"- Shareability decision: `{report.get('shareability', {}).get('decision')}`",
            f"- Safety report: `{open_first.parent / 'safety_report' / 'open_this_first_safety.md'}`",
        ]
    )
    if open_first.exists():
        open_first.write_text(open_first.read_text(encoding="utf-8") + summary + "\n", encoding="utf-8")


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


def visual_diagnose_inputs(args: argparse.Namespace) -> int:
    """Handle the 'visual-diagnose' subcommand."""
    input_path = Path(args.input)
    out_dir = Path(args.out)
    if not input_path.exists():
        print(f"input not found: {input_path}")
        return 1

    result = diagnose_visual_failure(input_path)
    confidence = result.get("confidence", 0.0)
    primary = result.get("primary_failure_type", "unknown")
    description = result.get("description", "")

    print("Agent Failure Doctor - Visual Diagnosis")
    print(f"Category: visual failure ({confidence:.0%})")
    print(f"Technical: visual_failure / {primary}")
    print(f"Description: {description}")
    print(f"\nFindings ({len(result.get('findings', []))}):")
    for finding in result.get("findings", []):
        print(f"  {finding}")
    if result.get("recommendations"):
        print(f"\nRecommendations ({len(result['recommendations'])}):")
        for rec in result["recommendations"]:
            print(f"  {rec}")
    if result.get("missing_evidence"):
        print(f"\nMissing evidence: {', '.join(result['missing_evidence'])}")

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "visual_diagnosis.json"
    write_json(report_path, result)
    if getattr(args, "ocr_provider", None):
        ocr_result = extract_ocr_evidence(
            input_path,
            out_dir / "ocr_evidence",
            provider=args.ocr_provider,
            safety_evaluate=True,
        )
        result["ocr_evidence"] = {
            "provider": ocr_result["ocr"].get("provider"),
            "shareability_decision": ocr_result["ocr"].get("safety", {}).get("shareability_decision"),
            "text_blocks": len(ocr_result["ocr"].get("text_blocks", [])),
        }
        write_json(report_path, result)
    print(f"\nReport: {report_path}")
    return 0


def visual_runtime_inputs(args: argparse.Namespace) -> int:
    command = args.visual_runtime_command
    try:
        if command == "diagnose":
            result = write_visual_runtime_report(
                Path(args.input),
                Path(args.out),
                no_dom=bool(args.no_dom),
                dom_optional=bool(args.dom_optional),
                safety_evaluate=bool(args.safety_evaluate),
            )
            diagnosis = result["diagnosis"]
            if getattr(args, "ocr_provider", None):
                ocr_result = extract_ocr_evidence(
                    Path(args.input),
                    Path(args.out) / "ocr_evidence",
                    provider=args.ocr_provider,
                    safety_evaluate=bool(args.safety_evaluate),
                )
                write_json(
                    Path(args.out) / "ocr_runtime_summary.json",
                    {
                        "provider": ocr_result["ocr"].get("provider"),
                        "shareability_decision": ocr_result["ocr"].get("safety", {}).get("shareability_decision"),
                        "ocr_step_confidence": ocr_result["ocr"].get("confidence_summary", {}).get("overall", 0.0),
                        "ocr_target_persistence": "available_if_text_repeats_across_steps",
                        "ocr_text_drift": "available_if_step_ocr_changes",
                        "ocr_vlm_conflict_rate": "available_when_vlm_responses_present",
                        "ocr_compression_loss_score": "available_when_screenshot_quality_metadata_present",
                    },
                )
            print("Agent Failure Doctor - Visual Runtime Diagnosis")
            print(f"Subtype: {diagnosis.get('subtype')} ({float(diagnosis.get('confidence', 0)):.0%})")
            print(f"Risk: {diagnosis.get('risk_level')}")
            print(f"Next: {diagnosis.get('safe_next_action')}")
            print(f"Output: {args.out}")
            return 0
        if command == "profile":
            run = load_visual_run(Path(args.input), no_dom=bool(args.no_dom), dom_optional=bool(args.dom_optional))
            profile = profile_visual_run(run)
            out_dir = Path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)
            write_json(out_dir / "visual_runtime_profile.json", profile)
            print("Agent Failure Doctor - Visual Runtime Profile")
            print(f"Frames: {profile.get('counts', {}).get('frames')}")
            print(f"Output: {out_dir}")
            return 0
        if command == "compare":
            report = compare_visual_runs(Path(args.baseline), Path(args.candidate), Path(args.out))
            print("Agent Failure Doctor - Visual Runtime Compare")
            print(report.get("recommendation"))
            print(f"Output: {args.out}")
            return 0
        if command == "adapt":
            summary = adapt_visual_artifacts(str(args.source), Path(args.input), Path(args.out), redact_images=bool(args.redact_images))
            print("Agent Failure Doctor - Visual Runtime Adapter")
            print(f"Source: {summary.get('source')}")
            print(f"Frames: {summary.get('frames')}")
            print(f"Output: {args.out}")
            return 0
        if command == "validate":
            report = validate_visual_run(Path(args.input), no_dom=bool(args.no_dom), dom_optional=bool(args.dom_optional))
            out_dir = Path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)
            write_json(out_dir / "visual_runtime_validation.json", report)
            print("Agent Failure Doctor - Visual Runtime Validate")
            print(f"Status: {report.get('status')}")
            print(f"Output: {out_dir}")
            return 0 if report.get("status") in {"pass", "warning"} else 1
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print(f"unsupported visual-runtime command: {command}")
    return 2


def regulated_eval_inputs(args: argparse.Namespace) -> int:
    try:
        payload = write_regulated_eval_report(args.suite, Path(args.out), case_id=args.case)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor - Regulated Evaluation")
    print(f"Suite: {payload.get('suite')}")
    print(f"Status: {payload.get('status')}")
    print(f"Cases: {payload.get('total_cases')}")
    print(f"Output: {args.out}")
    return 0 if payload.get("status") == "pass" else 1


def full_chain_eval_inputs(args: argparse.Namespace) -> int:
    try:
        out_dir = Path(args.out)
        if args.input:
            payload = write_full_chain_report(
                Path(args.input),
                out_dir,
                include_safety=bool(args.include_safety),
                include_ocr=bool(args.include_ocr),
                include_visual=bool(args.include_visual),
                include_regulated=bool(args.include_regulated),
            )
        else:
            out_dir.mkdir(parents=True, exist_ok=True)
            runs = [path for path in sorted(Path(args.batch).iterdir()) if path.is_dir()]
            reports = [
                write_full_chain_report(
                    run,
                    out_dir / run.name,
                    include_safety=bool(args.include_safety),
                    include_ocr=bool(args.include_ocr),
                    include_visual=bool(args.include_visual),
                    include_regulated=bool(args.include_regulated),
                )
                for run in runs
            ]
            payload = {
                "schema_version": "full_chain_batch_evaluation/v1",
                "version": "v3.6.0",
                "status": "pass" if all(report.get("status") == "pass" for report in reports) else "fail",
                "total_runs": len(reports),
                "reports": reports,
                "forbidden_output_count": 0,
                "private_solution_leak_count": 0,
                "real_platform_access_count": 0,
                "external_api_call_count": 0,
            }
            write_json(out_dir / "full_chain_batch_evaluation.json", payload)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("Agent Failure Doctor - Full-Chain Evaluation")
    print(f"Status: {payload.get('status')}")
    print(f"Version: {payload.get('version')}")
    print(f"Output: {args.out}")
    return 0 if payload.get("status") == "pass" else 1


def collect_inputs(path: Path) -> dict[str, Any]:
    files = [path] if path.is_file() else sorted(item for item in path.iterdir() if item.is_file())
    evidence: dict[str, Any] = {
        "source": str(path),
        "trace_zip": None,
        "logs": [],
        "network_events": [],
        "probe_reports": [],
        "runtime_reports": [],
        "script_reports": [],
        "descriptions": [],
        "screenshot_metadata": [],
        "unrecognized_files": [],
    }
    for file_path in files:
        lower = file_path.name.lower()
        if lower.endswith(".zip") and "trace" in lower:
            evidence["trace_zip"] = str(file_path)
        elif lower.endswith(".json") and (
            "js_integrity" in lower or "script_integrity" in lower or "bundle" in lower or "obfuscat" in lower
        ):
            evidence["script_reports"].extend(_read_script_reports(file_path))
        elif lower.endswith(".json") and (
            "runtime" in lower or "timing" in lower or "client_hint" in lower or "client-hint" in lower
        ):
            evidence["runtime_reports"].extend(_read_runtime_reports(file_path))
        elif lower.endswith(".json") and "probe" in lower:
            evidence["probe_reports"].extend(_read_probe_reports(file_path))
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
        "probe_reports": len(evidence.get("probe_reports", [])),
        "runtime_reports": len(evidence.get("runtime_reports", [])),
        "script_reports": len(evidence.get("script_reports", [])),
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
    if observed["probe_reports"]:
        priority.append("probe_report")
    if observed["runtime_reports"]:
        priority.append("runtime_report")
    if observed["script_reports"]:
        priority.append("script_report")
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
    probe_reports = evidence.get("probe_reports", [])
    probe_text = _probe_reports_to_text(probe_reports)
    runtime_reports = evidence.get("runtime_reports", [])
    runtime_text = _runtime_reports_to_text(runtime_reports)
    script_reports = evidence.get("script_reports", [])
    script_text = _script_reports_to_text(script_reports)
    log_text = "\n".join(
        part
        for part in [
            "\n".join(str(item.get("text", "")) for item in _prioritized_log_entries(log_entries)),
            probe_text,
            runtime_text,
            script_text,
        ]
        if part
    )
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
            "probe_reports": probe_reports[:5] if isinstance(probe_reports, list) else [],
            "runtime_reports": runtime_reports[:5] if isinstance(runtime_reports, list) else [],
            "script_reports": script_reports[:5] if isinstance(script_reports, list) else [],
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
    import re
    if 429 in statuses or re.search(r"\b429\b", text):
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
    return (
        not observed.get("trace_zip")
        and not observed.get("logs")
        and not observed.get("network_events")
        and not observed.get("probe_reports")
        and not observed.get("runtime_reports")
        and not observed.get("script_reports")
    )


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
        "probe_reports": [item.get("name") for item in evidence.get("probe_reports", []) if isinstance(item, Mapping)],
        "runtime_reports": [item.get("name") for item in evidence.get("runtime_reports", []) if isinstance(item, Mapping)],
        "script_reports": [item.get("name") for item in evidence.get("script_reports", []) if isinstance(item, Mapping)],
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
    if "probe_report" in priority:
        return "User-supplied probe_report.json was recognized as offline evidence; add logs, network.json, or trace.zip to improve context."
    if "runtime_report" in priority:
        return "User-supplied browser/runtime or input-timing report was recognized as offline evidence; add logs, network.json, or trace.zip to improve context."
    if "script_report" in priority:
        return "User-supplied JavaScript/request-integrity report was recognized as offline evidence; add logs, network.json, or trace.zip to improve context."
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


def _read_probe_reports(path: Path) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [{**parsed, "name": path.name}]
    if isinstance(parsed, list):
        return [{**item, "name": path.name} for item in parsed if isinstance(item, dict)]
    return []


def _read_runtime_reports(path: Path) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [{**parsed, "name": path.name}]
    if isinstance(parsed, list):
        return [{**item, "name": path.name} for item in parsed if isinstance(item, dict)]
    return []


def _read_script_reports(path: Path) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [{**parsed, "name": path.name}]
    if isinstance(parsed, list):
        return [{**item, "name": path.name} for item in parsed if isinstance(item, dict)]
    return []


def _probe_reports_to_text(reports: Any) -> str:
    if not isinstance(reports, list):
        return ""
    parts: list[str] = []
    for report in reports[:5]:
        if not isinstance(report, Mapping):
            continue
        transport = report.get("transport")
        if isinstance(transport, Mapping):
            if transport.get("tls_alpn_fingerprint_mismatch") is True:
                parts.append("TLS ALPN fingerprint mismatch: standard HTTP client and browser transport evidence differ.")
            if transport.get("transport_fingerprint_risk") is True:
                parts.append("transport fingerprint risk: TLS handshake, ALPN, HTTP version, and browser evidence differ.")
            if transport.get("http2_settings_fingerprint_mismatch") is True:
                parts.append("HTTP/2 SETTINGS fingerprint mismatch: standard client settings differ from browser protocol stack.")
            if transport.get("ja4_h2_fingerprint_mismatch") is True:
                parts.append("JA4 H2 fingerprint mismatch: protocol stack evidence differs from browser H2 evidence.")
            for key in (
                "alpn",
                "browser_alpn",
                "http_version",
                "browser_http_version",
                "ja3_string",
                "ja3_hash",
                "ja4_h2_summary",
                "http2_settings_summary",
            ):
                value = transport.get(key)
                if value:
                    parts.append(f"{key}={value}")
        ip_reputation = report.get("ip_reputation")
        if isinstance(ip_reputation, Mapping):
            classification = str(ip_reputation.get("classification") or "")
            if classification in {"hosting_or_vpn_risk", "low_hosting_ip", "uncertain"}:
                parts.append(f"ip reputation classification={classification}")
    return "\n".join(parts)[:1000]


def _runtime_reports_to_text(reports: Any) -> str:
    if not isinstance(reports, list):
        return ""
    parts: list[str] = []
    for report in reports[:5]:
        if not isinstance(report, Mapping):
            continue
        runtime = report.get("browser_runtime")
        if isinstance(runtime, Mapping):
            if runtime.get("client_hints_platform_mismatch") is True:
                parts.append("client hints platform mismatch: user-agent, Sec-CH-UA-Platform, and runtime platform evidence differ.")
            if runtime.get("browser_header_consistency_risk") is True:
                parts.append("browser header consistency risk: browser headers and runtime metadata conflict.")
            if runtime.get("canvas_fingerprint_collision") is True:
                parts.append("canvas fingerprint collision: duplicate canvas hash evidence repeats across sanitized sessions.")
            if runtime.get("browser_canvas_fingerprint_risk") is True:
                parts.append("browser canvas fingerprint risk: canvas hash uniqueness audit failed in authorized test telemetry.")
            if runtime.get("webgl_virtual_renderer_detected") is True:
                parts.append("WebGL virtual renderer detected: sanitized renderer/vendor evidence suggests virtualized browser runtime.")
            if runtime.get("webrtc_private_ip_leak_detected") is True:
                parts.append("WebRTC private IP leak detected: sanitized ICE candidate summary includes private network evidence.")
            if runtime.get("automation_global_scope_leak_detected") is True:
                parts.append("automation global scope leak detected: sanitized runtime summary found automation globals.")
            if runtime.get("runtime_sandbox_leak_detected") is True:
                parts.append("runtime sandbox leak detected: browser runtime summary exposes sandbox/global boundary leakage.")
            if runtime.get("native_function_integrity_mismatch") is True:
                parts.append("native function integrity mismatch: browser native reflection summary differs from expected runtime.")
            if runtime.get("debugger_timing_anomaly") is True:
                parts.append("debugger timing anomaly: sanitized runtime timing summary crosses the configured threshold.")
            for key in (
                "user_agent_platform",
                "sec_ch_ua_platform",
                "navigator_platform",
                "user_agent",
                "language",
                "webgl_renderer_family",
                "ice_candidate_summary",
                "global_scope_summary",
                "sandbox_summary",
                "native_reflection_summary",
                "debugger_timing_bucket",
            ):
                value = runtime.get(key)
                if value:
                    parts.append(f"{key}={value}")
            for key in ("duplicate_canvas_hash_count", "total_sessions", "evidence_source"):
                value = runtime.get(key)
                if value is not None:
                    parts.append(f"{key}={value}")
        timing = report.get("input_timing")
        if isinstance(timing, Mapping):
            if timing.get("zero_interval_input_detected") is True:
                parts.append("zero interval input detected: sanitized input timing summary reports impossible key intervals.")
            if timing.get("fixed_interval_input_detected") is True:
                parts.append("behavioral input risk: sanitized input timing summary reports fixed interval input timing.")
            if timing.get("keystroke_telemetry_anomaly") is True:
                parts.append("keystroke telemetry anomaly: sanitized input timing summary is inconsistent with interactive input.")
            if timing.get("pointer_trajectory_entropy_anomaly") is True:
                parts.append("pointer trajectory entropy anomaly: sanitized movement summary reports low vertical deviation.")
            if timing.get("mathematical_trajectory_detected") is True:
                parts.append("mathematical trajectory detected: sanitized pointer acceleration profile is too deterministic.")
            for key in (
                "average_key_interval_ms",
                "interval_variance_ms2",
                "input_method",
                "vertical_deviation_bucket",
                "acceleration_profile",
                "evidence_source",
            ):
                value = timing.get(key)
                if value is not None:
                    parts.append(f"{key}={value}")
    return "\n".join(parts)[:1000]


def _script_reports_to_text(reports: Any) -> str:
    if not isinstance(reports, list):
        return ""
    parts: list[str] = []
    for report in reports[:5]:
        if not isinstance(report, Mapping):
            continue
        integrity = report.get("script_integrity")
        if isinstance(integrity, Mapping):
            if integrity.get("obfuscated_js_integrity_required") is True:
                parts.append("obfuscated JS integrity required: protected script evidence gates request acceptance.")
            if integrity.get("js_ast_obfuscation_detected") is True:
                parts.append("JS AST obfuscation detected: sanitized bundle summary shows obfuscated request-integrity logic.")
            if integrity.get("rotated_string_array_detected") is True:
                parts.append("rotated string array detected: sanitized bundle summary shows string-array indirection.")
            if integrity.get("client_generated_token_missing") is True:
                parts.append("client generated token missing: request was rejected because script-produced integrity evidence is absent.")
            if integrity.get("request_integrity_algorithm_changed") is True:
                parts.append("request integrity algorithm changed: authorized regression shows token validation drift after a script update.")
            if integrity.get("js_vmp_integrity_check_failed") is True:
                parts.append("JS VMP integrity check failed: client VM signature mismatch in sanitized runtime report.")
            if integrity.get("numeric_semantics_mismatch") is True:
                parts.append("numeric semantics mismatch: client VM arithmetic semantics differ from the local verifier.")
            for key in (
                "http_status",
                "bundle_hash_prefix",
                "script_url_host",
                "evidence_source",
                "client_vm_summary",
                "numeric_semantics_summary",
            ):
                value = integrity.get(key)
                if value:
                    parts.append(f"{key}={value}")
    return "\n".join(parts)[:1000]


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
    import re
    m = re.search(r"\b(401|403|429|500|502|503)\b", text)
    if m:
        return int(m.group(1))
    return None


def _input_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "trace_zip": evidence.get("trace_zip"),
        "log_count": len(evidence.get("logs", [])),
        "network_event_count": len(evidence.get("network_events", [])),
        "runtime_report_count": len(evidence.get("runtime_reports", [])),
        "script_report_count": len(evidence.get("script_reports", [])),
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
