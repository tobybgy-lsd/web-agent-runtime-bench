from __future__ import annotations

from pathlib import Path

from .store import KnowledgeBase


def export_sanitized(kb: Path, out: Path) -> dict:
    return KnowledgeBase(kb).export_sanitized(out)
