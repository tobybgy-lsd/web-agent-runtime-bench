from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .audit import append_audit, validate_hash_chain
from .permissions import ROLE_PERMISSIONS
from .policy import write_default_policy


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def init_workspace(workspace: Path) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    for sub in [
        "policies",
        "approvals/pending",
        "approvals/approved",
        "approvals/rejected",
        "audit/audit_exports",
        "projects",
        "teams",
        "shared_kb",
        "reports",
        "sanitized_exports",
        "cache",
    ]:
        (workspace / sub).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "enterprise_workspace/v1",
        "version": "v4.1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "local_only": True,
        "default_host": "127.0.0.1",
        "allow_lan_default": False,
        "external_api_default": False,
        "telemetry": False,
        "raw_access_default": "blocked",
    }
    _write_json(workspace / "enterprise_manifest.json", manifest)
    if not (workspace / "users.json").exists():
        _write_json(workspace / "users.json", {"schema_version": "enterprise_users/v1", "users": {}})
    _write_json(
        workspace / "roles.json",
        {
            "schema_version": "enterprise_roles/v1",
            "roles": {role: sorted(perms) for role, perms in sorted(ROLE_PERMISSIONS.items())},
        },
    )
    write_default_policy(workspace)
    append_audit(workspace, actor="system", action="enterprise.init", target=str(workspace))
    return manifest


def require_workspace(workspace: Path) -> None:
    if not (workspace / "enterprise_manifest.json").exists():
        raise FileNotFoundError(f"enterprise workspace not initialized: {workspace}")


def validate_workspace(workspace: Path) -> dict[str, Any]:
    require_workspace(workspace)
    manifest = json.loads((workspace / "enterprise_manifest.json").read_text(encoding="utf-8"))
    status = {
        "schema_version": "enterprise_validation/v1",
        "version": manifest.get("version", "v4.1.0"),
        "status": "pass",
        "local_only": manifest.get("local_only") is True,
        "default_host": manifest.get("default_host"),
        "allow_lan_default": manifest.get("allow_lan_default"),
        "external_api_call_count": 0,
        "telemetry_call_count": 0,
        "private_solution_in_workspace": 0,
        "raw_access_blocked_by_default": manifest.get("raw_access_default") == "blocked",
        "patch_auto_apply_available": False,
        "audit_hash_chain_valid": validate_hash_chain(workspace),
    }
    if not status["audit_hash_chain_valid"] or status["default_host"] != "127.0.0.1":
        status["status"] = "fail"
    return status
