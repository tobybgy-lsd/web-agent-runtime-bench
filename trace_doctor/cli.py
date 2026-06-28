from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping
from zipfile import ZIP_DEFLATED, ZipFile

from tools.failure_artifacts.adapters import artifact_from_playwright_trace
from tools.failure_artifacts.diagnose import diagnose_artifact
from tools.failure_artifacts.issue import render_issue_draft
from tools.failure_artifacts.reporter import render_markdown_report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "diagnose":
        return diagnose_trace(args)
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trace_doctor",
        description="Local-first diagnostic tool for sanitized Playwright trace.zip failures.",
    )
    sub = parser.add_subparsers(dest="command")

    diagnose = sub.add_parser("diagnose", help="Diagnose a local sanitized Playwright trace.zip")
    diagnose.add_argument("trace_zip", help="Path to local sanitized trace.zip")
    diagnose.add_argument("--out", required=True, help="Output directory for the diagnostic report")
    diagnose.add_argument("--run-id", default=None, help="Stable run identifier")
    return parser


def diagnose_trace(args: argparse.Namespace) -> int:
    trace_zip = Path(args.trace_zip)
    out_dir = Path(args.out)
    if not trace_zip.exists():
        print(f"trace.zip not found: {trace_zip}")
        return 1

    artifact = artifact_from_playwright_trace(trace_zip, run_id=args.run_id)
    diagnosis = diagnose_artifact(artifact)
    artifact["labels"] = {
        "failure_type": diagnosis.get("failure_type", "unknown"),
        "confidence": diagnosis.get("confidence", 0.0),
    }

    outputs = write_trace_doctor_report(out_dir, artifact, diagnosis)
    confidence = float(diagnosis.get("confidence", 0.0))
    print("Playwright Trace Failure Doctor")
    print(f"Failure type: {diagnosis.get('failure_type', 'unknown')} ({confidence:.0%})")
    print(f"Report: {out_dir}")
    print(f"Bundle: {outputs['trace_doctor_report.zip']}")
    return 0


def write_trace_doctor_report(out_dir: Path, artifact: Mapping[str, Any], diagnosis: Mapping[str, Any]) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "failure_artifact.json": out_dir / "failure_artifact.json",
        "diagnosis.json": out_dir / "diagnosis.json",
        "diagnosis.md": out_dir / "diagnosis.md",
        "evidence.json": out_dir / "evidence.json",
        "issue_draft.md": out_dir / "issue_draft.md",
        "repair_suggestions.md": out_dir / "repair_suggestions.md",
        "trace_doctor_report.zip": out_dir / "trace_doctor_report.zip",
    }
    outputs["failure_artifact.json"].write_text(_json(artifact), encoding="utf-8")
    outputs["diagnosis.json"].write_text(_json(diagnosis), encoding="utf-8")
    outputs["diagnosis.md"].write_text(render_markdown_report(diagnosis, artifact), encoding="utf-8")
    outputs["evidence.json"].write_text(_json(_evidence_payload(artifact, diagnosis)), encoding="utf-8")
    outputs["issue_draft.md"].write_text(render_issue_draft(artifact, diagnosis, _doctor_summary(diagnosis)), encoding="utf-8")
    outputs["repair_suggestions.md"].write_text(_render_repair_suggestions(diagnosis), encoding="utf-8")
    _write_report_zip(out_dir, outputs["trace_doctor_report.zip"])
    return outputs


def _evidence_payload(artifact: Mapping[str, Any], diagnosis: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": artifact.get("run_id"),
        "tool": artifact.get("tool"),
        "failure_type": diagnosis.get("failure_type"),
        "confidence": diagnosis.get("confidence"),
        "evidence": diagnosis.get("evidence", []),
        "observations": artifact.get("observations", {}),
        "error": artifact.get("error", {}),
        "artifacts": artifact.get("artifacts", {}),
        "safety": artifact.get("safety", {}),
    }


def _doctor_summary(diagnosis: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ready": True,
        "checks": [{"name": "trace_doctor", "status": "pass", "detail": "local trace diagnosis generated"}],
        "errors": [],
        "next_steps": ["review diagnosis, evidence, and repair suggestions before sharing"],
        "diagnosis": dict(diagnosis),
    }


def _render_repair_suggestions(diagnosis: Mapping[str, Any]) -> str:
    fixes = diagnosis.get("suggested_fix", [])
    if not isinstance(fixes, list) or not fixes:
        fixes = ["Collect more local evidence and inspect the trace manually."]
    lines = ["# Suggested Repair", ""]
    for item in fixes:
        text = str(item)
        if "\n" in text:
            lines.extend([text, ""])
        else:
            lines.append(f"- {text}")
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- Do not add CAPTCHA bypass logic.",
            "- Do not extract credentials, cookies, tokens, or authorization headers.",
            "- Keep the diagnostic workflow local and based on sanitized traces.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_report_zip(root: Path, zip_path: Path) -> None:
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(root.iterdir()):
            if path == zip_path or not path.is_file():
                continue
            archive.write(path, path.name)


def _json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
