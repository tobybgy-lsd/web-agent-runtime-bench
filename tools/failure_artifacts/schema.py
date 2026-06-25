"""Compatibility layer for failure artifact schema operations."""

from __future__ import annotations

from pathlib import Path

from .artifact import load_artifact as _load_artifact
from .artifact import validate_artifact as _validate_artifact


def load_artifact(path: Path | str) -> dict:
    return _load_artifact(path)


def validate_artifact(path: Path | str) -> list[str]:
    artifact_path = Path(path)
    return _validate_artifact(_load_artifact(artifact_path), base_dir=artifact_path.parent)
