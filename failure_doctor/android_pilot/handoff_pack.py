from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_handoff_pack(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_pilot_handoff_pack", VERSION, out, **kwargs)
