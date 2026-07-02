from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_data_mapping(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_pilot_data_mapping", VERSION, out, **kwargs)
