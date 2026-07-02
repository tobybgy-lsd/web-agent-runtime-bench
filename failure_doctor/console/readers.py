from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .redaction import redact_value


SECTION_FILES: dict[str, list[str]] = {
    "diagnosis": ["diagnosis.json", "diagnosis.md"],
    "evidence": ["evidence.json"],
    "repair_suggestions": ["repair_suggestions.md", "fix_plan.md"],
    "issue_draft": ["issue_draft.md"],
    "ai_handoff": ["codex_fix_prompt.md", "ai_handoff.json", "ai_handoff_safety.json"],
    "patch_proposal": ["patch_proposal.json", "patch_safety_report.json"],
    "visual_runtime": ["visual_runtime_profile.json", "visual_diagnosis.json"],
    "ocr_document": ["ocr_evidence.json", "ocr_diagnosis.json"],
    "regulated_workflow": ["regulated_eval_result.json", "regulated_report.json"],
    "batch_fleet": ["batch_summary.json", "batch_report.json"],
    "full_chain": ["full_chain_eval.json", "full_chain_report.json"],
    "verification": ["verification_report.json"],
    "sanitize": ["shareability_decision.json", "sanitize_report.json"],
    "safety": ["safety_evaluation_report.json", "safety_report.json"],
}


def _read_file(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        try:
            return {"kind": "json", "content": redact_value(json.loads(path.read_text(encoding="utf-8")))}
        except json.JSONDecodeError:
            return {"kind": "text", "content": redact_value(path.read_text(encoding="utf-8", errors="replace"))}
    return {"kind": "text", "content": redact_value(path.read_text(encoding="utf-8", errors="replace"))}


def _read_section(report_dir: Path, names: list[str]) -> dict[str, Any]:
    for name in names:
        path = report_dir / name
        if path.exists() and path.is_file():
            payload = _read_file(path)
            payload.update({"available": True, "file": name})
            return payload
    return {"available": False, "reason": "missing"}


def _summary_from_diagnosis(section: dict[str, Any]) -> dict[str, Any]:
    if not section.get("available"):
        return {
            "user_facing_category": "Evidence unavailable",
            "technical_category": "insufficient_evidence",
            "subtype": "insufficient_evidence",
            "confidence": 0.0,
            "next_action": "Import a Failure Doctor report or sanitized failure pack.",
        }
    content = section.get("content")
    if isinstance(content, dict):
        return {
            "user_facing_category": content.get("user_facing_category")
            or content.get("category")
            or "Automation failure",
            "technical_category": content.get("technical_category")
            or content.get("failure_type")
            or content.get("category")
            or "unknown",
            "subtype": content.get("subtype") or content.get("failure_subtype") or "unknown",
            "confidence": content.get("confidence", content.get("confidence_score", 0.0)),
            "next_action": content.get("next_action") or "Review evidence and safe repair plan.",
        }
    return {
        "user_facing_category": "Report available",
        "technical_category": "markdown_report",
        "subtype": "markdown_report",
        "confidence": 0.5,
        "next_action": "Review diagnosis.md and evidence files.",
    }


def read_console_report(report_dir: Path | str) -> dict[str, Any]:
    root = Path(report_dir).expanduser().resolve()
    sections = {name: _read_section(root, files) for name, files in SECTION_FILES.items()}
    return {
        "status": "ok" if root.exists() else "missing",
        "report_path": str(root),
        "summary": _summary_from_diagnosis(sections["diagnosis"]),
        "sections": sections,
        "raw_hidden_by_default": True,
        "shareable_outputs_only": True,
    }


def build_report_index(report_dirs: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for report_dir in report_dirs:
        report = read_console_report(report_dir)
        rows.append(
            {
                "id": report_dir.name,
                "path": str(report_dir),
                "summary": report["summary"],
                "available_sections": [
                    name for name, section in report["sections"].items() if section.get("available")
                ],
            }
        )
    return rows
