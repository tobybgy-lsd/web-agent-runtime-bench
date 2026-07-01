from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .forms import form_structure_from_ocr
from .layout import document_structure_from_ocr
from .quality import build_ocr_data_quality_report
from .table import table_structure_from_ocr


def write_ocr_report(out_dir: Path, ocr: dict[str, Any]) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    document = document_structure_from_ocr(ocr)
    table = table_structure_from_ocr(ocr)
    form = form_structure_from_ocr(ocr)
    quality = build_ocr_data_quality_report(ocr)
    safety = {
        "schema_version": "ocr_safety/v1",
        "status": ocr["safety"]["shareability_decision"],
        "local_only": ocr["safety"]["local_only"],
        "cloud_upload_used": ocr["safety"]["cloud_upload_used"],
        "redaction_status": ocr["safety"]["redaction_status"],
        "sensitive_findings": ocr["safety"].get("sensitive_findings", []),
    }
    files = {
        "ocr_evidence.json": out_dir / "ocr_evidence.json",
        "document_structure.json": out_dir / "document_structure.json",
        "table_structure.json": out_dir / "table_structure.json",
        "form_structure.json": out_dir / "form_structure.json",
        "ocr_data_quality_report.json": out_dir / "ocr_data_quality_report.json",
        "ocr_safety_report.json": out_dir / "ocr_safety_report.json",
        "ocr_evidence.md": out_dir / "ocr_evidence.md",
    }
    _write(files["ocr_evidence.json"], ocr)
    _write(files["document_structure.json"], document)
    _write(files["table_structure.json"], table)
    _write(files["form_structure.json"], form)
    _write(files["ocr_data_quality_report.json"], quality)
    _write(files["ocr_safety_report.json"], safety)
    files["ocr_evidence.md"].write_text(_render_md(ocr, quality), encoding="utf-8")
    return files


def write_handoff_summary(out_dir: Path, ocr: dict[str, Any]) -> Path:
    handoff_dir = out_dir / "ai_handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    path = handoff_dir / "ocr_evidence_summary.md"
    lines = ["# OCR Evidence Summary", "", "OCR evidence is supporting evidence, not ground truth.", ""]
    for block in ocr.get("text_blocks", [])[:20]:
        text = str(block.get("text", ""))
        if ocr.get("safety", {}).get("shareability_decision") != "safe_to_share":
            text = "[redacted]"
        lines.extend(
            [
                f"- finding_id: {block.get('id')}",
                f"  text_redacted: {text}",
                f"  bbox: {block.get('bbox')}",
                f"  confidence: {block.get('confidence')}",
                "  related_failure_type: ocr_evidence",
                "  safe_next_action: compare OCR evidence with DOM, VLM, or schema locally.",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _render_md(ocr: dict[str, Any], quality: dict[str, Any]) -> str:
    lines = [
        "# OCR Evidence",
        "",
        "OCR evidence is supporting evidence, not ground truth.",
        "",
        f"Provider: `{ocr.get('provider')}`",
        f"Mode: `{ocr.get('provider_mode')}`",
        f"Shareability: `{ocr.get('safety', {}).get('shareability_decision')}`",
        f"Cloud upload used: `{ocr.get('safety', {}).get('cloud_upload_used')}`",
        f"Text blocks: `{len(ocr.get('text_blocks', []))}`",
        f"Tables: `{len(ocr.get('tables', []))}`",
        f"Forms: `{len(ocr.get('forms', []))}`",
        f"Data-quality findings: `{quality.get('finding_count')}`",
    ]
    return "\n".join(lines) + "\n"
