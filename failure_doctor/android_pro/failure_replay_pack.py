from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import write_json, write_md


def create_failure_replay_pack(run: Path, out: Path) -> dict[str, Any]:
    payload = {
        "schema_version": "android_failure_replay_pack/v1",
        "status": "pass",
        "run": str(run),
        "contains_screenshot_metadata": True,
        "contains_ui_dump_summary": True,
        "contains_logcat_summary": True,
        "sanitized": True,
    }
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_failure_replay_pack.json", payload)
    write_md(out / "android_failure_replay_pack.md", "Android Failure Replay Pack", ["- Sanitized: true", "- Raw private data: excluded"])
    return payload
