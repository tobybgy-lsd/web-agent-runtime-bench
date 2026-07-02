from __future__ import annotations

from pathlib import Path

from .store import KnowledgeBase


def validate_kb(kb: Path) -> dict:
    return KnowledgeBase(kb).status()
