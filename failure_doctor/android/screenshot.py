from __future__ import annotations

from pathlib import Path
from typing import Any


def screenshot_metadata(path: Path | str) -> dict[str, Any]:
    screenshot = Path(path)
    return {"path": str(screenshot), "exists": screenshot.exists(), "bytes": screenshot.stat().st_size if screenshot.exists() else 0}
