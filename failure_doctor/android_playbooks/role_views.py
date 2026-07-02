from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_role_views(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_playbooks_role_views", VERSION, out, **kwargs)
