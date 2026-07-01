from __future__ import annotations

from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding
from .policy import UNSAFE_HANDOFF_PATTERNS


def evaluate_ai_handoff(root: Path | None) -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        text = lower_text(path)
        hits = [pattern for pattern in UNSAFE_HANDOFF_PATTERNS if pattern in text]
        if not hits:
            continue
        findings.append(
            SafetyFinding(
                id=f"finding_handoff_{len(findings)+1:03d}",
                type="unsafe_handoff",
                severity="high",
                evidence=[f"Unsafe AI handoff instruction in {rel(path, root)}: {', '.join(hits[:4])}"],
                affected_files=[rel(path, root)],
                decision="block",
                safe_next_action="Rewrite the handoff to diagnose, sanitize, use official APIs, request authorization, or stop if unauthorized.",
                forbidden_actions=hits,
            )
        )
    return findings
