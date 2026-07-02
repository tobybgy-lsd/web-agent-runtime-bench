from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def append_audit(farm: Path, action: str, payload: dict[str, Any]) -> None:
    farm.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": utc_now(),
        "schema_version": "android_ops_audit/v1",
        "action": action,
        "local_only": True,
        "no_upload": True,
        **payload,
    }
    with (farm / "audit_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

