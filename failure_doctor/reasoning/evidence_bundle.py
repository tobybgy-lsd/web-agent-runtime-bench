from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import BUNDLE_SCHEMA, TOOL_VERSION
from .safety import scan_text


SOURCE_MAP = {
    "diagnosis.json": "diagnosis",
    "evidence.json": "evidence",
    "input_summary.json": "evidence",
    "similar_cases.json": "kb",
    "ci_summary.json": "ci",
    "safety_evaluation_report.json": "safety",
    "visual_runtime_diagnosis.json": "visual",
    "ocr_evidence.json": "ocr",
    "regulated_eval_result.json": "regulated",
    "full_chain_eval.json": "full_chain",
}


def build_evidence_bundle(input_report: Path) -> dict[str, Any]:
    input_report = input_report.resolve()
    items: list[dict[str, Any]] = []
    for path in _candidate_files(input_report):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        summary = _summarize(payload)
        if not summary:
            continue
        scan = scan_text(summary)
        if not scan["is_allowed"]:
            continue
        evidence_id = f"E{len(items) + 1:03d}"
        items.append(
            {
                "evidence_id": evidence_id,
                "source": SOURCE_MAP.get(path.name, "report"),
                "summary": summary[:800],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "severity": _severity(payload),
                "confidence": _confidence(payload),
                "supports": [],
                "contradicts": [],
                "raw_excluded": True,
            }
        )
    safety = {
        "shareability_decision": "safe_to_share" if items else "sanitize_required",
        "reasoning_allowed": bool(items),
        "blocked_reason": None if items else "no_sanitized_evidence",
    }
    return {
        "schema_version": BUNDLE_SCHEMA,
        "tool_version": TOOL_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_report": str(input_report),
        "sanitized_only": True,
        "raw_content_excluded": True,
        "safety": safety,
        "evidence_items": items,
    }


def _candidate_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    names = set(SOURCE_MAP)
    return [path for path in sorted(root.rglob("*.json")) if path.name in names]


def _summarize(payload: Any) -> str:
    if isinstance(payload, dict):
        parts: list[str] = []
        for key in (
            "user_facing_category",
            "technical_category",
            "subtype",
            "failure_type",
            "failure_layer",
            "next_action",
            "confidence_reason",
            "status",
            "summary",
        ):
            value = payload.get(key)
            if value not in (None, "", [], {}):
                parts.append(f"{key}: {value}")
        if not parts and payload:
            for key, value in list(payload.items())[:8]:
                if isinstance(value, (str, int, float, bool)):
                    parts.append(f"{key}: {value}")
        return "; ".join(parts)
    return ""


def _severity(payload: Any) -> str:
    text = json.dumps(payload, ensure_ascii=False).lower()
    if "critical" in text:
        return "critical"
    if "high" in text:
        return "high"
    if "medium" in text:
        return "medium"
    return "low"


def _confidence(payload: Any) -> float:
    if isinstance(payload, dict):
        value = payload.get("confidence")
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value)))
    return 0.75
