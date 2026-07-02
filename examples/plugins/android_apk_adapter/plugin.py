from __future__ import annotations

from pathlib import Path
from typing import Any

from failure_doctor.android.normalizer import normalize_android_input


def collect(input_dir: str, out_dir: str, **_: Any) -> dict[str, Any]:
    return normalize_android_input(Path(input_dir), Path(out_dir))
