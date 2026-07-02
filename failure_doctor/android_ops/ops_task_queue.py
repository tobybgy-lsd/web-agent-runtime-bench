from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ops_audit import write_json


def init_queue(out: Path) -> dict[str, Any]:
    payload = {"schema_version": "android_ops_task_queue/v1", "status": "ready", "tasks": [], "checkpoints": []}
    return write_json(out / "ops_task_queue.json", payload)


def load_tasks(queue: Path) -> list[dict[str, Any]]:
    if queue.is_dir():
        path = queue / "bound_tasks.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")).get("tasks", [])
        path = queue / "tasks.jsonl"
    else:
        path = queue
    if not path.exists():
        return []
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("tasks", payload if isinstance(payload, list) else [])

