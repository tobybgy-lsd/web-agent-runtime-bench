from __future__ import annotations

from pathlib import Path

from .store import KnowledgeBase


def import_report(kb: Path, report: Path) -> dict:
    return KnowledgeBase(kb).import_report(report)
