"""Regression corpus helper for sanitized failure packs."""

from __future__ import annotations

import shutil
from pathlib import Path


def add_to_corpus(src: Path | str, sanitize: bool = True) -> dict:
    src_path = Path(src)
    artifact_path = src_path / "failure_artifact.json"
    if not artifact_path.exists():
        return {"ok": False, "error": "failure_artifact.json not found"}
    case_id = src_path.name
    root = Path("failure_corpus") / ("sanitized" if sanitize else "raw")
    dst = root / case_id
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src_path, dst)
    return {"ok": True, "case_id": case_id, "corpus_path": str(dst)}
