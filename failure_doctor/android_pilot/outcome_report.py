from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_outcome_report(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_pilot_outcome_report", VERSION, out, **kwargs)
