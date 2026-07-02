from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_android_compatibility(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("mobile_stability_android_compatibility", VERSION, out, **kwargs)
