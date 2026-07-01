from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def compare_ocr_dom(ocr_report_dir: Path, dom_path: Path, out_dir: Path) -> dict[str, Any]:
    ocr = json.loads((ocr_report_dir / "ocr_evidence.json").read_text(encoding="utf-8"))
    dom_text = _strip_html(dom_path.read_text(encoding="utf-8", errors="replace")) if dom_path.exists() else ""
    ocr_texts = [block.get("text", "") for block in ocr.get("text_blocks", []) if block.get("text")]
    findings: list[dict[str, Any]] = []
    for text in ocr_texts:
        if text and text.lower() not in dom_text.lower():
            findings.append({"type": "ocr_dom_text_conflict", "ocr_text": text, "severity": "medium"})
    for form in ocr.get("forms", []):
        for field in form.get("fields", []):
            label = str(field.get("label", ""))
            if label and label.lower() not in dom_text.lower():
                findings.append({"type": "ocr_form_label_value_mismatch", "label": label, "severity": "medium"})
    report = {
        "schema_version": "ocr_dom_consistency/v1",
        "status": "pass" if not findings else "warning",
        "ocr_text_count": len(ocr_texts),
        "dom_present": bool(dom_text),
        "findings": findings,
        "confidence": 0.94 if findings else 0.86,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ocr_dom_consistency_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "ocr_dom_consistency_report.md").write_text(_render_consistency_md("OCR-DOM Consistency", report), encoding="utf-8")
    return report


def compare_ocr_vlm(ocr_report_dir: Path, vlm_path: Path, out_dir: Path) -> dict[str, Any]:
    ocr = json.loads((ocr_report_dir / "ocr_evidence.json").read_text(encoding="utf-8"))
    vlm_text = "\n".join(_read_jsonl_texts(vlm_path)) if vlm_path.exists() else ""
    findings: list[dict[str, Any]] = []
    for block in ocr.get("text_blocks", []):
        text = str(block.get("text", ""))
        if text and vlm_text and text.lower() not in vlm_text.lower():
            findings.append({"type": "ocr_vlm_semantic_conflict", "ocr_text": text, "severity": "medium"})
    report = {
        "schema_version": "ocr_vlm_consistency/v1",
        "status": "pass" if not findings else "warning",
        "vlm_present": bool(vlm_text),
        "findings": findings,
        "confidence": 0.93 if findings else 0.84,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ocr_vlm_consistency_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def _read_jsonl_texts(path: Path) -> list[str]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            values.append(line)
            continue
        values.append(" ".join(str(v) for v in item.values() if isinstance(v, (str, int, float))))
    return values


def _render_consistency_md(title: str, report: dict[str, Any]) -> str:
    lines = [f"# {title}", "", f"Status: {report['status']}", "", "OCR evidence is supporting evidence, not ground truth.", ""]
    for finding in report.get("findings", []):
        lines.append(f"- {finding.get('type')}: {finding.get('ocr_text') or finding.get('label')}")
    return "\n".join(lines) + "\n"
