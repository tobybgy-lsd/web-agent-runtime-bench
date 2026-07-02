from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_console_integration(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_real_pilot_console_integration", VERSION, out, **kwargs)
