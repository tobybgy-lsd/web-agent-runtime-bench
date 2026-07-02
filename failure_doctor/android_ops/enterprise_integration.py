from __future__ import annotations

from pathlib import Path
from typing import Any

from .ops_audit import write_json


DEFAULT_POLICY = {
    "android_ops": {
        "default_mode": "dry_run",
        "allow_final_submit_default": False,
        "allow_business_mutation_default": False,
        "real_device_run_requires_role": ["rpa_operator", "qa_engineer", "enterprise_admin"],
        "business_mutation_requires_approval": True,
        "export_raw_screenshot": "blocked",
        "device_farm_admin_roles": ["enterprise_admin", "security_admin"],
    }
}


def validate_enterprise_policy(out: Path, policy: dict[str, Any] | None = None) -> dict[str, Any]:
    effective = policy or DEFAULT_POLICY
    android = effective.get("android_ops", {})
    status = "pass" if android.get("default_mode") == "dry_run" and android.get("export_raw_screenshot") == "blocked" else "fail"
    payload = {
        "schema_version": "android_ops_enterprise_policy/v1",
        "status": status,
        "policy": effective,
        "audit_required": True,
        "business_mutation_requires_approval": android.get("business_mutation_requires_approval") is True,
    }
    return write_json(out / "android_ops_enterprise_policy.json", payload)

