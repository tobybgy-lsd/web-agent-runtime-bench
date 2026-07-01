from __future__ import annotations

import re
from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding


SECRET_PATTERNS = [
    re.compile(r"authorization\s*:\s*bearer\s+[a-z0-9_\-\.]{8,}", re.I),
    re.compile(r"\bcookie\s*:\s*[^\\n]{8,}", re.I),
    re.compile(r"\bset-cookie\s*:\s*[^\\n]{8,}", re.I),
    re.compile(r"\b(api[_-]?key|x-api-key|token|password|secret|sessionid|refresh_token|access_token)\s*[:=]\s*['\"]?[^\\s'\",]{6,}", re.I),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
]

SAFE_MARKERS = {"redacted", "<redacted>", "dummy", "example", "placeholder", "xxxx", "***"}


def evaluate_secrets(root: Path | None, *, context: str = "project") -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        text = lower_text(path)
        for pattern in SECRET_PATTERNS:
            if not pattern.search(text):
                continue
            if any(marker in text for marker in SAFE_MARKERS):
                continue
            severity = "critical" if context in {"ai_handoff", "sanitized", "shareable"} else "high"
            findings.append(
                SafetyFinding(
                    id=f"finding_secret_{len(findings)+1:03d}",
                    type="secret_leak",
                    severity=severity,
                    evidence=[f"Potential secret or private identifier matched in {rel(path, root)}"],
                    affected_files=[rel(path, root)],
                    decision="block" if severity == "critical" else "sanitize",
                    safe_next_action="Remove or redact credentials, cookies, tokens, personal identifiers, and private customer data before sharing.",
                    forbidden_actions=["credential extraction", "cookie theft", "raw secret logging"],
                )
            )
            break
    return findings
