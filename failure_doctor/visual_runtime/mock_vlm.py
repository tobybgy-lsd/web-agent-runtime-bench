from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def mock_vlm_observe(visual_run_dir: Path) -> list[dict[str, Any]]:
    labels = visual_run_dir / "mock_vlm_labels.json"
    if labels.exists():
        data = json.loads(labels.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    responses = visual_run_dir / "vlm_responses.jsonl"
    if responses.exists():
        rows: list[dict[str, Any]] = []
        for line in responses.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                if isinstance(item, dict):
                    rows.append(item)
        return rows
    return [{"step_id": 1, "summary": "offline mock visual observation", "confidence": 0.5}]


def call_vlm_api(*_: Any, **__: Any) -> dict[str, Any]:
    return {
        "status": "disabled",
        "reason": "External VLM calls are disabled by default. Configure and authorize a provider explicitly outside this mock path.",
        "external_vlm_call_count": 0,
        "screenshot_upload_count": 0,
    }
