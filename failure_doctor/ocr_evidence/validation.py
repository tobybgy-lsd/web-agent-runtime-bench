from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def validate_ocr_report(report_dir: Path, out_dir: Path | None = None) -> dict[str, Any]:
    evidence_path = report_dir / "ocr_evidence.json"
    findings: list[str] = []
    if not evidence_path.exists():
        findings.append("missing_ocr_evidence_json")
        ocr: dict[str, Any] = {}
    else:
        ocr = json.loads(evidence_path.read_text(encoding="utf-8"))
    required = ["schema_version", "tool_version", "provider", "provider_mode", "input", "safety", "text_blocks", "tables", "forms"]
    for key in required:
        if key not in ocr:
            findings.append(f"missing_{key}")
    safety = ocr.get("safety", {})
    if safety.get("cloud_upload_used"):
        findings.append("cloud_upload_used")
    if safety.get("shareability_decision") == "safe_to_share" and safety.get("redaction_status") not in {"not_needed", "redacted"}:
        findings.append("invalid_shareability_redaction_state")
    report = {
        "schema_version": "ocr_validation_result/v1",
        "status": "pass" if not findings else "fail",
        "findings": findings,
        "text_block_count": len(ocr.get("text_blocks", [])),
        "table_count": len(ocr.get("tables", [])),
        "form_count": len(ocr.get("forms", [])),
        "external_ocr_call_count": 0,
        "document_upload_count": 0,
        "real_platform_access_count": 0,
    }
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "ocr_validation_result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
