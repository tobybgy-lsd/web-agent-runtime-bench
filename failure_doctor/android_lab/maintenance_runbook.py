from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_maintenance_runbook(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_lab_maintenance_runbook", VERSION, out, **kwargs)
