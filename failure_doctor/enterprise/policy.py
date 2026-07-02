from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "version": "enterprise_policy/v1",
    "network": {
        "default_host": "127.0.0.1",
        "allow_lan_default": False,
        "external_api_default": False,
        "telemetry": False,
    },
    "raw_access": {"default": "blocked", "approval_required": True},
    "handoff": {"default": "approval_required", "allow_if_safety_pass": True},
    "share_pack": {"default": "sanitized_only"},
    "patch": {"auto_apply": False, "proposal_only": True, "approval_required": True},
    "kb": {"import_default": "sanitized_only", "export_default": "sanitized_only", "raw_export": "blocked"},
    "reasoning": {"provider_default": "mock_reasoner", "cloud_reasoner": "blocked"},
    "ci": {"artifact_policy": "sanitized_only", "fail_on": ["private_solution_leak", "forbidden_output"]},
    "audit": {"required": True, "immutable_append_only": True},
}


def policy_dir(workspace: Path) -> Path:
    return workspace / "policies"


def write_default_policy(workspace: Path) -> None:
    path = policy_dir(workspace) / "enterprise_policy.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(DEFAULT_POLICY, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_policy(workspace: Path) -> dict[str, Any]:
    path = policy_dir(workspace) / "enterprise_policy.json"
    if not path.exists():
        write_default_policy(workspace)
    return json.loads(path.read_text(encoding="utf-8"))


def list_policies(workspace: Path) -> dict[str, Any]:
    return {
        "schema_version": "enterprise_policy_list/v1",
        "policies": sorted(p.name for p in policy_dir(workspace).glob("*") if p.is_file()),
        "active_policy": load_policy(workspace),
    }


def set_policy(workspace: Path, source: Path) -> dict[str, Any]:
    text = source.read_text(encoding="utf-8")
    target = policy_dir(workspace) / "enterprise_policy.yml"
    target.write_text(text, encoding="utf-8")
    return {"status": "updated", "policy": str(target)}
