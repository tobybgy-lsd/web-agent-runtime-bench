from __future__ import annotations

from pathlib import Path


def audit_log_path(kb: Path) -> Path:
    return kb / "audit_log.jsonl"
