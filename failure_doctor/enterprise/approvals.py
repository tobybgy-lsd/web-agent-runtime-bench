from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .audit import append_audit
from .workspace import require_workspace


def _next_request_id(workspace: Path) -> str:
    existing = list((workspace / "approvals" / "pending").glob("req_*.json"))
    existing += list((workspace / "approvals" / "approved").glob("req_*.json"))
    existing += list((workspace / "approvals" / "rejected").glob("req_*.json"))
    return f"req_{len(existing) + 1:03d}"


def create_request(workspace: Path, request_type: str, target_ref: str, created_by: str = "system") -> dict:
    require_workspace(workspace)
    request_id = _next_request_id(workspace)
    payload = {
        "schema_version": "approval_request/v1",
        "request_id": request_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": created_by,
        "request_type": request_type,
        "target_ref": target_ref,
        "risk_level": "low",
        "policy_decision": "approval_required",
        "status": "pending",
    }
    path = workspace / "approvals" / "pending" / f"{request_id}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    append_audit(workspace, actor=created_by, action=f"approval.request.{request_type}", target=request_id)
    return payload


def decide_request(workspace: Path, request_id: str, decision: str, reason: str = "") -> dict:
    require_workspace(workspace)
    if decision not in {"approve", "reject"}:
        raise ValueError("decision must be approve or reject")
    source = workspace / "approvals" / "pending" / f"{request_id}.json"
    if not source.exists():
        raise FileNotFoundError(f"approval request not found: {request_id}")
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["status"] = "approved" if decision == "approve" else "rejected"
    payload["decided_at"] = datetime.now(timezone.utc).isoformat()
    payload["decision_reason"] = reason
    target_dir = workspace / "approvals" / payload["status"]
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    source.unlink()
    append_audit(workspace, actor="system", action=f"approval.{decision}", target=request_id, decision=decision)
    return payload
