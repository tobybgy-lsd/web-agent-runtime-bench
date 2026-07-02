from __future__ import annotations

from pathlib import Path

from .store import KnowledgeBase


def promote_fix(kb: Path, case_id: str, verification: Path) -> dict:
    return KnowledgeBase(kb).promote_fix(case_id, verification)
