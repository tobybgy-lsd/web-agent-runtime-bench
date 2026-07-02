from __future__ import annotations

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "viewer": {"report.view_sanitized", "policy.view"},
    "developer": {
        "report.view_sanitized",
        "diagnosis.run",
        "patch.propose",
        "reasoning.view_validated",
        "kb.view",
        "approval.request",
    },
    "rpa_operator": {"collect.run", "diagnosis.run", "report.view_sanitized", "approval.request"},
    "qa_engineer": {"verify.run", "ci.view", "approval.request"},
    "incident_lead": {
        "report.view_sanitized",
        "handoff.export",
        "share.export_sanitized",
        "audit.view",
        "approval.approve_low",
    },
    "compliance_reviewer": {
        "report.view_sanitized",
        "share.export_sanitized",
        "audit.view",
        "audit.export_sanitized",
        "approval.approve_low",
    },
    "security_admin": {
        "policy.view",
        "policy.edit",
        "audit.view",
        "audit.export_sanitized",
        "audit.export_full_local",
        "raw_access.approve",
        "approval.approve_high",
    },
    "kb_curator": {"kb.view", "kb.import", "kb.promote_fix", "kb.export_sanitized"},
    "ci_admin": {"ci.view", "ci.run", "ci.policy_edit", "policy.view"},
    "enterprise_admin": {
        "console.admin",
        "policy.view",
        "policy.edit",
        "audit.view",
        "audit.export_sanitized",
        "approval.approve_low",
        "approval.approve_high",
        "kb.export_sanitized",
    },
}


def list_roles() -> list[dict[str, object]]:
    return [
        {"role": role, "permissions": sorted(permissions)}
        for role, permissions in sorted(ROLE_PERMISSIONS.items())
    ]


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
