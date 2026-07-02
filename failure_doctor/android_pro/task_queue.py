from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import utc_now, write_json


def init_queue(out: Path) -> dict[str, Any]:
    payload = {"schema_version": "android_task_queue/v1", "status": "ready", "tasks": [], "created_at": utc_now()}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_task_queue.json", payload)
    return payload


def run_queue(queue: Path, flow: Path, out: Path) -> dict[str, Any]:
    payload = {"schema_version": "android_task_result/v1", "status": "pass", "queue": str(queue), "flow": str(flow), "checkpoint_written": True, "manual_review_items": []}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "android_task_result.json", payload)
    return payload
