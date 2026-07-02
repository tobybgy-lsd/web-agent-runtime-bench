from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json
from .safety import contains_business_mutation, contains_final_action, scan_forbidden_text


def evaluate_mutation_guard(flow: Path, out: Path) -> dict[str, Any]:
    text = flow.read_text(encoding="utf-8") if flow.exists() else str(flow)
    scan_text = _strip_safe_false_config(text)
    final = contains_final_action(scan_text) or "allow_final_submit: true" in text.lower()
    mutation = contains_business_mutation(scan_text) or "allow_business_mutation: true" in text.lower()
    forbidden = scan_forbidden_text(scan_text)
    blocked = final or mutation or bool(forbidden)
    reasons = []
    if final:
        reasons.append("android_final_submit_blocked")
    if mutation:
        reasons.append("android_business_mutation_blocked")
    if forbidden:
        reasons.append("forbidden_android_ops_text")
    payload = {
        "schema_version": "android_mutation_guard/v1",
        "status": "blocked" if blocked else "pass",
        "final_submit_blocked": final,
        "business_mutation_blocked": mutation,
        "allow_save_draft": True,
        "allow_dry_run": True,
        "blocked_reasons": reasons,
        "forbidden_terms": forbidden,
        "real_business_mutation_count": 0,
    }
    return write_json(out / "android_mutation_guard_report.json", payload)


def _strip_safe_false_config(text: str) -> str:
    safe_lines = []
    for line in text.splitlines():
        lowered = line.strip().lower()
        if lowered in {"allow_final_submit: false", "allow_business_mutation: false"}:
            continue
        safe_lines.append(line)
    return "\n".join(safe_lines)
