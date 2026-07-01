from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .models import SafetyFinding


SENSITIVE_PATH_MARKERS = [
    "appdata",
    "google\\chrome\\user data",
    "microsoft\\edge\\user data",
    "mozilla\\firefox\\profiles",
    ".ssh",
    "credential",
    "cookies",
    "login data",
    "local state",
]


def is_broad_or_sensitive_scope(path: Path) -> bool:
    resolved = path.expanduser().resolve()
    text = str(resolved).lower()
    home = Path.home().resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved.relative_to(temp_root)
        return any(marker in text for marker in SENSITIVE_PATH_MARKERS if marker not in {"appdata"})
    except ValueError:
        pass
    if resolved.anchor and str(resolved) == resolved.anchor:
        return True
    if resolved == home:
        return True
    if resolved.name.lower() in {"desktop", "downloads"} and resolved.parent == home:
        return True
    return any(marker in text for marker in SENSITIVE_PATH_MARKERS)


def evaluate_scope(path: Path | None, allow_broad_scope: bool = False) -> list[SafetyFinding]:
    if path is None:
        return []
    findings: list[SafetyFinding] = []
    if is_broad_or_sensitive_scope(path):
        findings.append(
            SafetyFinding(
                id="finding_scope_001",
                type="scope_violation",
                severity="high",
                evidence=[f"Input scope is broad or sensitive: {path}"],
                affected_files=[str(path)],
                decision="block" if not allow_broad_scope else "manual_review",
                safe_next_action="Choose a narrow project folder. Never scan browser profiles, credential stores, or whole-computer paths.",
                forbidden_actions=["whole-computer scanning", "browser profile reading", "credential store reading"],
            )
        )
    return findings


def safe_project_audit(path: Path | None) -> dict[str, bool]:
    return {
        "local_only": True,
        "no_external_upload": True,
        "no_active_probe": True,
        "no_browser_profile_access": True,
        "no_credential_store_access": True,
        "project_scoped_only": not is_broad_or_sensitive_scope(path) if path else True,
        "no_upload": True,
        "no_network": True,
    }
