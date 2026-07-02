from __future__ import annotations

from pathlib import Path

from .store import KnowledgeBase


def match_report(kb: Path, report: Path, out: Path | None = None) -> dict:
    return KnowledgeBase(kb).match_report(report, out)
