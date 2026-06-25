#!/usr/bin/env python
"""warb - Web Automation Repair Bench CLI.

Commands:
  diagnose  <failure_artifact.json>   Classify failure and generate report
  collect   --tool <tool> --input <dir> --out <dir>   Create a basic artifact
  pack      --tool <tool> --input <dir> --out <dir>   Sanitize, diagnose, and zip a pack
  report    <diagnosis.json>          Generate HTML report
  regression add <dir>                Add sanitized case to corpus
  validate  <failure_artifact.json>   Validate artifact schema
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.failure_artifacts.classifier import classify_failure_artifact
from tools.failure_artifacts.collector import collect_from_dir
from tools.failure_artifacts.packager import package_failure_dir
from tools.failure_artifacts.regression import add_to_corpus
from tools.failure_artifacts.reporter import render_html_report, render_markdown_report
from tools.failure_artifacts.schema import load_artifact, validate_artifact


def _c(code: str, text: str) -> str:
    try:
        import os

        if os.name == "nt":
            return text
    except Exception:
        pass
    return f"\033[{code}m{text}\033[0m"


GREEN = lambda text: _c("32", text)
YELLOW = lambda text: _c("33", text)
RED = lambda text: _c("31", text)
BOLD = lambda text: _c("1", text)
DIM = lambda text: _c("2", text)


def cmd_diagnose(args: argparse.Namespace) -> int:
    artifact_path = Path(args.artifact)
    if not artifact_path.exists():
        print(RED(f"File not found: {artifact_path}"))
        return 1

    errors = validate_artifact(artifact_path)
    if errors:
        print(YELLOW("Schema warnings:"))
        for error in errors:
            print(f"  - {error}")
        print()

    artifact = load_artifact(artifact_path)
    diagnosis = classify_failure_artifact(artifact)
    _print_diagnosis(diagnosis, artifact)

    default_out_dir = ROOT / "sample_run" / "diagnosis" / str(artifact.get("run_id", artifact_path.stem))
    out_dir = Path(args.out_dir) if args.out_dir else default_out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    diag_json = out_dir / "diagnosis.json"
    diag_md = out_dir / "diagnosis.md"
    diag_html = out_dir / "diagnosis_report.html"
    repair_md = out_dir / "repair_prompt.md"

    diag_json.write_text(json.dumps(diagnosis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    diag_md.write_text(render_markdown_report(diagnosis, artifact), encoding="utf-8")
    diag_html.write_text(render_html_report(diagnosis, artifact), encoding="utf-8")
    repair_md.write_text(_render_repair_prompt(diagnosis, artifact), encoding="utf-8")

    print()
    print(DIM(f"  diagnosis.json  -> {diag_json}"))
    print(DIM(f"  diagnosis.md    -> {diag_md}"))
    print(DIM(f"  diagnosis.html  -> {diag_html}"))
    print(DIM(f"  repair_prompt   -> {repair_md}"))
    return 0


def _print_diagnosis(diagnosis: dict, artifact: dict) -> None:
    failure_type = diagnosis.get("failure_type", "unknown")
    confidence = float(diagnosis.get("confidence", 0))
    tool = artifact.get("tool", "unknown")
    run_id = artifact.get("run_id", "-")
    confidence_colour = GREEN if confidence >= 0.8 else (YELLOW if confidence >= 0.5 else RED)

    print()
    print(BOLD("  WebAgentRuntimeBench - Failure Diagnosis"))
    print(DIM(f"  Run: {run_id}  |  Tool: {tool}"))
    print()
    print(f"  Failure type:  {BOLD(failure_type)}")
    print(f"  Confidence:    {confidence_colour(f'{confidence:.0%}')}")
    print()

    evidence = diagnosis.get("evidence", [])
    if evidence:
        print("  Evidence:")
        for item in evidence:
            print(f"    - {item}")
        print()

    fixes = diagnosis.get("suggested_fix", [])
    if fixes:
        print("  Suggested fix:")
        for item in fixes:
            print(f"    -> {item}")
        print()

    if diagnosis.get("can_auto_fix", False):
        print(GREEN("  Auto-fix may be possible - see repair_prompt.md"))
    else:
        print(DIM("  Manual fix required - see repair_prompt.md"))


def _render_repair_prompt(diagnosis: dict, artifact: dict) -> str:
    failure_type = diagnosis.get("failure_type", "unknown")
    evidence = "\n".join(f"- {item}" for item in diagnosis.get("evidence", []))
    fixes = "\n".join(f"- {item}" for item in diagnosis.get("suggested_fix", []))
    tool = artifact.get("tool", "unknown")
    return f"""## Repair Task: {failure_type}

You are a coding assistant helping fix a failed web automation run.

### Tool
{tool}

### Failure Type
{failure_type} (confidence: {float(diagnosis.get('confidence', 0)):.0%})

### Evidence
{evidence}

### Suggested Fix Direction
{fixes}

### Instructions
1. Read the evidence above carefully.
2. Locate the relevant code in the user's scraper.
3. Apply the minimal fix that addresses the root cause.
4. Do not modify unrelated code.
5. Do not add credentials, tokens, or bypass logic.
6. Explain what you changed and why.
"""


def cmd_collect(args: argparse.Namespace) -> int:
    input_dir = Path(args.input)
    out_dir = Path(args.out)
    if not input_dir.exists():
        print(RED(f"Input directory not found: {input_dir}"))
        return 1
    artifact = collect_from_dir(input_dir, tool=args.tool)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "failure_artifact.json"
    out_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(GREEN(f"Artifact written: {out_path}"))
    print(f"Run ID: {artifact.get('run_id')}")
    print(f"Tool:   {artifact.get('tool')}")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    input_dir = Path(args.input)
    out_dir = Path(args.out)
    try:
        result = package_failure_dir(
            input_dir,
            out_dir,
            tool=args.tool,
            run_id=args.run_id,
            summary=args.summary,
            required_fields=args.required_field,
            status_code=args.status_code,
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(RED(str(exc)))
        return 1

    diagnosis = result["diagnosis"]
    print(GREEN(f"Failure pack written: {out_dir}"))
    print(f"Artifact: {result['artifact_path']}")
    print(f"Issue:    {result['issue_path']}")
    print(f"Zip:      {result['zip_path']}")
    print(f"Initial diagnosis: {diagnosis.get('failure_type')} ({float(diagnosis.get('confidence', 0)):.0%})")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    diag_path = Path(args.diagnosis)
    if not diag_path.exists():
        print(RED(f"File not found: {diag_path}"))
        return 1
    diagnosis = json.loads(diag_path.read_text(encoding="utf-8"))
    artifact_path = diag_path.parent.parent / "failure_artifact.json"
    artifact = load_artifact(artifact_path) if artifact_path.exists() else {}
    out_path = diag_path.parent / "diagnosis_report.html"
    out_path.write_text(render_html_report(diagnosis, artifact), encoding="utf-8")
    print(GREEN(f"HTML report: {out_path}"))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.artifact)
    if not path.exists():
        print(RED(f"File not found: {path}"))
        return 1
    errors = validate_artifact(path)
    if errors:
        print(YELLOW(f"{len(errors)} schema issue(s):"))
        for error in errors:
            print(f"  - {error}")
        return 1
    print(GREEN("Artifact is valid"))
    return 0


def cmd_regression(args: argparse.Namespace) -> int:
    if args.regression_command != "add":
        print("Unknown regression command")
        return 1
    src = Path(args.src)
    if not src.exists():
        print(RED(f"Directory not found: {src}"))
        return 1
    result = add_to_corpus(src, sanitize=not args.no_sanitize)
    if result["ok"]:
        print(GREEN(f"Added to corpus: {result['corpus_path']}"))
        print(f"Case ID: {result['case_id']}")
        return 0
    print(RED(f"Failed: {result.get('error')}"))
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="warb",
        description="Web Automation Repair Bench - failure diagnosis and regression CLI",
    )
    sub = parser.add_subparsers(dest="command")

    diagnose = sub.add_parser("diagnose", help="Classify a failure artifact and generate reports")
    diagnose.add_argument("artifact", help="Path to failure_artifact.json")
    diagnose.add_argument("--out-dir", default=None, help="Output directory; defaults to sample_run/diagnosis/<run_id>")

    collect = sub.add_parser("collect", help="Create a basic failure artifact from a directory")
    collect.add_argument("--tool", default="unknown", help="Tool name: playwright, scrapy, requests, node, other")
    collect.add_argument("--input", required=True, help="Directory containing failed run files")
    collect.add_argument("--out", required=True, help="Output directory for failure_artifact.json")

    pack = sub.add_parser("pack", help="Sanitize, diagnose, and zip a shareable failure pack")
    pack.add_argument("--tool", default="unknown", help="Tool name: playwright, scrapy, requests, node, other")
    pack.add_argument("--input", required=True, help="Directory containing failed run files")
    pack.add_argument("--out", required=True, help="Output directory for sanitized pack")
    pack.add_argument("--run-id", default=None, help="Stable pack identifier; defaults to pack_<timestamp>")
    pack.add_argument("--summary", default="Collected sanitized failure pack", help="Short failure summary")
    pack.add_argument("--status-code", type=int, default=None, help="HTTP status code observed at failure time")
    pack.add_argument("--required-field", action="append", default=[], help="Expected output field; repeat for multiple fields")

    report = sub.add_parser("report", help="Generate HTML report from diagnosis.json")
    report.add_argument("diagnosis", help="Path to diagnosis.json")

    validate = sub.add_parser("validate", help="Validate failure_artifact.json schema")
    validate.add_argument("artifact", help="Path to failure_artifact.json")

    regression = sub.add_parser("regression", help="Manage regression corpus")
    regression_sub = regression.add_subparsers(dest="regression_command")
    regression_add = regression_sub.add_parser("add", help="Add a failure run to regression corpus")
    regression_add.add_argument("src", help="Directory containing failure_artifact.json + diagnosis.json")
    regression_add.add_argument("--no-sanitize", action="store_true", help="Skip sanitized corpus path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    dispatch = {
        "diagnose": cmd_diagnose,
        "collect": cmd_collect,
        "pack": cmd_pack,
        "report": cmd_report,
        "validate": cmd_validate,
        "regression": cmd_regression,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
