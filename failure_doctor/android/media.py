from __future__ import annotations

from pathlib import Path
from typing import Any


def describe_media(path: Path | str) -> dict[str, Any]:
    media = Path(path)
    return {"path": str(media), "exists": media.exists(), "bytes": media.stat().st_size if media.exists() else 0}
