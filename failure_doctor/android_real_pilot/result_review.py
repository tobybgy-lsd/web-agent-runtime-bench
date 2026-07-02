from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_result_review(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_real_pilot_result_review", VERSION, out, **kwargs)
