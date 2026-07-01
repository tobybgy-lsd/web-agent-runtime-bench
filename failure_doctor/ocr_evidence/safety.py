from __future__ import annotations

import re
from pathlib import Path
from typing import Any


SENSITIVE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("authorization_header", r"\bauthorization\s*[:=]\s*bearer\s+[a-z0-9._\-]+"),
    ("cookie", r"\bcookie\s*[:=]"),
    ("token", r"\b(token|api[_-]?key|secret)\s*[:=]\s*[a-z0-9._\-]{6,}"),
    ("email", r"\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b"),
    ("phone", r"\b(?:\+?\d[\d\-\s]{8,}\d)\b"),
    ("customer_data", r"\b(customer|client|buyer|recipient|id\s*card|身份证|客户|订单)\b"),
    ("order_data", r"\b(order[_ -]?id|invoice|sku|quantity|订单|发票)\b"),
)


def scan_text_for_sensitive_data(text: str) -> list[str]:
    lowered = text.lower()
    findings: list[str] = []
    for name, pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            findings.append(name)
    return sorted(set(findings))


def scan_payload_for_sensitive_data(payload: Any) -> list[str]:
    chunks: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            chunks.append(value)

    walk(payload)
    return scan_text_for_sensitive_data("\n".join(chunks))


def scan_input_path(path: Path, max_bytes: int = 1_000_000) -> list[str]:
    chunks: list[str] = []
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    for file_path in files:
        if file_path.suffix.lower() not in {".txt", ".json", ".jsonl", ".md", ".html", ".csv"}:
            continue
        try:
            chunks.append(file_path.read_text(encoding="utf-8", errors="replace")[:max_bytes])
        except OSError:
            continue
    return scan_text_for_sensitive_data("\n".join(chunks))


def safety_decision(*, provider: str, input_findings: list[str], ocr_findings: list[str], allow_cloud: bool) -> dict[str, Any]:
    findings = sorted(set(input_findings + ocr_findings))
    is_cloud = provider.startswith("baidu_cloud")
    if is_cloud and not allow_cloud:
        return {
            "local_only": False,
            "cloud_upload_used": False,
            "safety_evaluated": True,
            "redaction_status": "blocked",
            "shareability_decision": "blocked",
            "blocked_reason": "cloud_provider_requires_explicit_allow_cloud_ocr",
            "sensitive_findings": findings,
        }
    if is_cloud and findings:
        return {
            "local_only": False,
            "cloud_upload_used": False,
            "safety_evaluated": True,
            "redaction_status": "blocked",
            "shareability_decision": "blocked",
            "blocked_reason": "sensitive_input_blocks_cloud_ocr",
            "sensitive_findings": findings,
        }
    if findings:
        return {
            "local_only": not is_cloud,
            "cloud_upload_used": False,
            "safety_evaluated": True,
            "redaction_status": "redacted",
            "shareability_decision": "sanitize_required",
            "sensitive_findings": findings,
        }
    return {
        "local_only": not is_cloud,
        "cloud_upload_used": False,
        "safety_evaluated": True,
        "redaction_status": "not_needed",
        "shareability_decision": "safe_to_share",
        "sensitive_findings": [],
    }
