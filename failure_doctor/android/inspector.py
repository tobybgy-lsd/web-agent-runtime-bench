from __future__ import annotations

from pathlib import Path
from typing import Any

from .normalizer import normalize_android_input


def inspect_android_evidence(path: Path | str) -> dict[str, Any]:
    return normalize_android_input(path, Path(path) / ".android_inspection" if Path(path).is_dir() else Path(path).parent / ".android_inspection")
