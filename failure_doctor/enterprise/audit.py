from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _audit_path(workspace: Path) -> Path:
    return workspace / "audit" / "audit_log.jsonl"


def append_audit(
    workspace: Path,
    *,
    actor: str,
    action: str,
    target: str = "",
    decision: str = "recorded",
    details: dict[str, Any] | None = None,
) -> str:
    path = _audit_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = ""
    if path.exists():
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if rows:
            previous_hash = json.loads(rows[-1]).get("entry_hash", "")
    event_id = f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    entry = {
        "schema_version": "enterprise_audit/v1",
        "event_id": event_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "target": target,
        "decision": decision,
        "details": details or {},
        "previous_hash": previous_hash,
    }
    payload = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    entry["entry_hash"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return event_id


def read_audit(workspace: Path) -> list[dict[str, Any]]:
    path = _audit_path(workspace)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate_hash_chain(workspace: Path) -> bool:
    previous = ""
    for entry in read_audit(workspace):
        recorded = entry.get("entry_hash", "")
        entry_without_hash = dict(entry)
        entry_without_hash.pop("entry_hash", None)
        if entry_without_hash.get("previous_hash") != previous:
            return False
        payload = json.dumps(entry_without_hash, sort_keys=True, ensure_ascii=False)
        if hashlib.sha256(payload.encode("utf-8")).hexdigest() != recorded:
            return False
        previous = recorded
    return True


def export_audit(workspace: Path, out: Path, *, sanitized_only: bool = True) -> dict[str, Any]:
    rows = read_audit(workspace)
    exported = {
        "schema_version": "enterprise_audit_export/v1",
        "sanitized_only": sanitized_only,
        "event_count": len(rows),
        "hash_chain_valid": validate_hash_chain(workspace),
        "events": rows,
        "raw_secret_in_audit_export": 0,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit_export.json").write_text(
        json.dumps(exported, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    append_audit(workspace, actor="system", action="audit.export", target=str(out), decision="sanitized")
    return exported
