from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_lab_workspace(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_lab_lab_workspace", VERSION, out, **kwargs)
