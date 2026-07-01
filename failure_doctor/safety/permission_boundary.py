from __future__ import annotations

from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding


PERMISSION_PATTERNS = [
    "read outside project",
    "read browser profile",
    "credential store",
    "full env dump",
    "upload raw artifact",
    "execute shell from page",
    "disable security settings",
    "turn off sandbox",
    "run unknown binary",
]


def evaluate_permission_boundary(root: Path | None) -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        text = lower_text(path)
        hits = [pattern for pattern in PERMISSION_PATTERNS if pattern in text]
        if not hits:
            continue
        findings.append(
            SafetyFinding(
                id=f"finding_permission_{len(findings)+1:03d}",
                type="permission_boundary",
                severity="high",
                evidence=[f"Permission boundary risk in {rel(path, root)}: {', '.join(hits[:4])}"],
                affected_files=[rel(path, root)],
                decision="block",
                safe_next_action="Keep automation project-scoped and local-only; do not read browser profiles, credential stores, full env dumps, or protected system paths.",
                forbidden_actions=hits,
            )
        )
    return findings
