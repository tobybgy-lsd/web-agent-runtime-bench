from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .audit import append_audit
from .permissions import ROLE_PERMISSIONS
from .workspace import require_workspace


def _path(workspace: Path) -> Path:
    return workspace / "users.json"


def _load(workspace: Path) -> dict:
    require_workspace(workspace)
    return json.loads(_path(workspace).read_text(encoding="utf-8"))


def _save(workspace: Path, payload: dict) -> None:
    _path(workspace).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_user(workspace: Path, username: str, role: str) -> dict:
    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"unknown role: {role}")
    data = _load(workspace)
    data.setdefault("users", {})[username] = {
        "username": username,
        "role": role,
        "disabled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(workspace, data)
    append_audit(workspace, actor="system", action="user.add", target=username, details={"role": role})
    return data["users"][username]


def disable_user(workspace: Path, username: str) -> dict:
    data = _load(workspace)
    if username not in data.get("users", {}):
        raise ValueError(f"unknown user: {username}")
    data["users"][username]["disabled"] = True
    _save(workspace, data)
    append_audit(workspace, actor="system", action="user.disable", target=username)
    return data["users"][username]


def list_users(workspace: Path) -> dict:
    return _load(workspace)
