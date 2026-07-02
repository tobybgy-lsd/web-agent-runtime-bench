from __future__ import annotations

from pathlib import Path
from typing import Any

from failure_doctor.adapters.core import diagnose_adapter_input, normalize_adapter_input


def normalize(input_path: Path, out_dir: Path) -> dict[str, Any]:
    return normalize_adapter_input(input_path, out_dir, kind="api")


def diagnose(input_path: Path, out_dir: Path) -> dict[str, Any]:
    return diagnose_adapter_input(input_path, out_dir, kind="api")
