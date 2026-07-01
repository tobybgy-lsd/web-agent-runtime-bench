from __future__ import annotations

from .models import SafetyFinding
from .policy import PRIVATE_CONTENT_PATTERNS


def decide_shareability(findings: list[SafetyFinding], text_index: str = "") -> dict[str, object]:
    lower = text_index.lower()
    private_hits = [pattern for pattern in PRIVATE_CONTENT_PATTERNS if pattern in lower]
    if private_hits:
        return {
            "decision": "blocked",
            "reason": "private_solution_or_training_content_detected",
            "allowed_outputs": ["safety_evaluation_report.md", "open_this_first_safety.md"],
            "blocked_outputs": ["raw artifacts", "AI handoff", "patch proposal"],
        }
    if any(item.severity == "critical" or item.decision == "block" for item in findings):
        return {
            "decision": "blocked",
            "reason": "critical_or_blocking_finding",
            "allowed_outputs": ["safety_evaluation_report.md", "open_this_first_safety.md"],
            "blocked_outputs": ["raw artifacts", "AI handoff", "patch proposal"],
        }
    if findings:
        return {
            "decision": "sanitize_required",
            "reason": "findings_require_redaction_or_manual_review",
            "allowed_outputs": ["safety_evaluation_report.md", "sanitized summaries"],
            "blocked_outputs": ["raw local artifacts"],
        }
    return {
        "decision": "safe_to_share",
        "reason": "no_safety_findings",
        "allowed_outputs": ["safety_evaluation_report.md", "sanitized_failure_pack", "AI handoff after review"],
        "blocked_outputs": [],
    }
