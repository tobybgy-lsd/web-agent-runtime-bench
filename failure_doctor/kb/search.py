from __future__ import annotations

from pathlib import Path

from .store import KnowledgeBase


def search(kb: Path, query: str) -> list[dict]:
    return KnowledgeBase(kb).search(query)
