from __future__ import annotations

from pathlib import Path
from typing import Any

from . import VERSION
from ._common import safe_report


def run_flow_editor_model(out: Path, **kwargs: Any) -> dict[str, Any]:
    return safe_report("android_authoring_flow_editor_model", VERSION, out, **kwargs)
