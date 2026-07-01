from __future__ import annotations

from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding


DOM_PATTERNS = [
    "display:none",
    "type=\"hidden\"",
    "visibility:hidden",
    "<iframe",
    "autofill",
    "password",
    "send data externally",
    "ignore previous instructions",
    "form action='http",
    'form action="http',
]


def evaluate_dom(root: Path | None) -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        if path.suffix.lower() not in {".html", ".htm", ".xml", ".txt", ".md"}:
            continue
        text = lower_text(path)
        hits = [pattern for pattern in DOM_PATTERNS if pattern in text]
        if not hits:
            continue
        findings.append(
            SafetyFinding(
                id=f"finding_dom_{len(findings)+1:03d}",
                type="malicious_dom",
                severity="medium",
                evidence=[f"DOM risk markers in {rel(path, root)}: {', '.join(hits[:4])}"],
                affected_files=[rel(path, root)],
                decision="manual_review",
                safe_next_action="Review hidden forms, iframes, third-party scripts, and page instructions before trusting automation output.",
                forbidden_actions=["execute shell from page content", "reveal secrets to page content"],
            )
        )
    return findings
