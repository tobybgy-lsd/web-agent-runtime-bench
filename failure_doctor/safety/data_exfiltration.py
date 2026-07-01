from __future__ import annotations

from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding


EXFILTRATION_PATTERNS = [
    "customer_name",
    "customer name",
    "order_id",
    "order id",
    "phone",
    "email",
    "ssn",
    "id number",
    "private page table",
    "send data externally",
    "full pii payload",
]


def evaluate_data_exfiltration(root: Path | None) -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        text = lower_text(path)
        hits = [pattern for pattern in EXFILTRATION_PATTERNS if pattern in text]
        if not hits:
            continue
        findings.append(
            SafetyFinding(
                id=f"finding_exfiltration_{len(findings)+1:03d}",
                type="data_exfiltration",
                severity="high",
                evidence=[f"Potential page/customer data exposure in {rel(path, root)}: {', '.join(hits[:4])}"],
                affected_files=[rel(path, root)],
                decision="sanitize",
                safe_next_action="Remove customer, order, page table, and personal data from shareable artifacts and AI handoff prompts.",
                forbidden_actions=["page data exfiltration", "raw customer data sharing"],
            )
        )
    return findings
