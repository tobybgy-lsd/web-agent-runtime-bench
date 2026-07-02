from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import write_json, write_md


def write_android_pro_report(out: Path, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / f"{name}.json", payload)
    write_md(out / f"{name}.md", "Android Pro Report", [f"- Status: {payload.get('status', 'unknown')}"])
    return payload
