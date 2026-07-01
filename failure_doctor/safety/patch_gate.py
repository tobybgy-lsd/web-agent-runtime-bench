from __future__ import annotations

from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding
from .policy import UNSAFE_PATCH_PATTERNS


def evaluate_patch(root: Path | None) -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        text = lower_text(path)
        hits = [pattern for pattern in UNSAFE_PATCH_PATTERNS if pattern in text]
        if not hits:
            continue
        findings.append(
            SafetyFinding(
                id=f"finding_patch_{len(findings)+1:03d}",
                type="unsafe_patch",
                severity="high",
                evidence=[f"Unsafe patch proposal in {rel(path, root)}: {', '.join(hits[:4])}"],
                affected_files=[rel(path, root)],
                decision="block",
                safe_next_action="Keep patch proposals limited to normal bug fixes, official API integration, schema validation, dedupe, checkpointing, retries, or manual review gates.",
                forbidden_actions=hits,
            )
        )
    return findings
