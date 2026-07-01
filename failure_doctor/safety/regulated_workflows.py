from __future__ import annotations

from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding


REGULATED_MARKERS = ["finance", "approval", "gov", "healthcare", "erp", "ecommerce", "medical"]
REGULATED_RISK_MARKERS = ["pii", "ssn", "customer", "patient", "order id", "private data", "approval state mismatch", "raw log"]


def evaluate_regulated_workflow(root: Path | None) -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        text = lower_text(path)
        name = path.name.lower()
        if not (any(marker in text for marker in REGULATED_MARKERS) or any(marker in name for marker in REGULATED_MARKERS)):
            continue
        hits = [pattern for pattern in REGULATED_RISK_MARKERS if pattern in text]
        if not hits:
            continue
        findings.append(
            SafetyFinding(
                id=f"finding_regulated_{len(findings)+1:03d}",
                type="regulated_workflow_risk",
                severity="high",
                evidence=[f"Regulated workflow mock risk in {rel(path, root)}: {', '.join(hits[:4])}"],
                affected_files=[rel(path, root)],
                decision="manual_review",
                safe_next_action="Use local-only mock evidence, redact PII, keep audit trails, and avoid connecting to real finance, government, healthcare, or ERP systems.",
                forbidden_actions=["real regulated system access", "raw PII sharing"],
            )
        )
    return findings
