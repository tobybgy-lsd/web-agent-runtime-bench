from __future__ import annotations

from pathlib import Path

from .store import KnowledgeBase


def rebuild(path: Path) -> dict:
    return KnowledgeBase(path).rebuild_indexes()
