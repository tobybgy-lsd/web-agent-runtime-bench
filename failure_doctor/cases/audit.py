from __future__ import annotations

import json
from pathlib import Path

from .models import utc_now


def append_case_audit(workspace: Path, action: str, payload: dict) -> None:
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    audit_path = workspace / "case_audit.jsonl"
    record = {"created_at": utc_now(), "action": action, "payload": payload}
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
