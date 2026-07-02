from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .manifest import load_manifest
from .models import (
    ALL_PERMISSIONS,
    FORBIDDEN_PERMISSIONS,
    HIGH_RISK_PERMISSIONS,
    HOOKS,
    PLUGIN_SCHEMA_VERSION,
    PLUGIN_TYPES,
)
from .security import scan_text_files


PLUGIN_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


def validate_plugin(plugin_dir: Path, *, write_report: bool = True) -> dict[str, Any]:
    plugin_dir = Path(plugin_dir)
    issues: list[str] = []
    warnings: list[str] = []
    unsafe_blocked = False
    high_risk_permissions: list[str] = []

    if not plugin_dir.exists() or not plugin_dir.is_dir():
        return _write_or_return(plugin_dir, _failed(["plugin directory not found"]), write_report)

    manifest_file = plugin_dir / "plugin_manifest.json"
    if not manifest_file.exists():
        return _write_or_return(plugin_dir, _failed(["plugin_manifest.json missing"]), write_report)

    try:
        manifest, payload = load_manifest(plugin_dir)
    except (json.JSONDecodeError, OSError, TypeError) as exc:
        return _write_or_return(plugin_dir, _failed([f"manifest unreadable: {exc}"]), write_report)

    if manifest.schema_version != PLUGIN_SCHEMA_VERSION:
        issues.append("invalid schema_version")
    if not PLUGIN_ID_RE.match(manifest.plugin_id):
        issues.append("invalid plugin_id")
    if manifest.type not in PLUGIN_TYPES:
        issues.append("invalid plugin type")
    if not manifest.local_only:
        issues.append("local_only must be true")
    if not manifest.no_upload:
        issues.append("no_upload must be true")
    if not manifest.no_external_api:
        issues.append("no_external_api must be true")
    if manifest.requires_network:
        issues.append("requires_network is blocked by default")
    if manifest.requires_shell:
        issues.append("requires_shell is blocked by default")
    if manifest.requires_write_access:
        warnings.append("requires_write_access is high risk and requires enterprise approval")

    if not manifest.entrypoint or not (plugin_dir / manifest.entrypoint).exists():
        issues.append("entrypoint missing")

    schemas = payload.get("schemas", {})
    for key in ("input", "output"):
        schema_path = schemas.get(key)
        if not schema_path or not (plugin_dir / str(schema_path)).exists():
            issues.append(f"{key} schema missing")

    if not manifest.permissions:
        issues.append("permissions missing")
    for permission in manifest.permissions:
        if permission in FORBIDDEN_PERMISSIONS:
            issues.append(f"forbidden permission: {permission}")
        elif permission not in ALL_PERMISSIONS:
            issues.append(f"unknown permission: {permission}")
        if permission in HIGH_RISK_PERMISSIONS:
            high_risk_permissions.append(permission)
            if permission in {"network_access", "run_local_command", "read_raw_evidence"}:
                issues.append(f"{permission} is blocked by default")

    if not manifest.hooks:
        issues.append("hooks missing")
    for hook in manifest.hooks:
        if hook not in HOOKS:
            issues.append(f"unknown hook: {hook}")

    safety = manifest.safety
    if safety.get("forbidden_actions_declared") is not True:
        issues.append("safety.forbidden_actions_declared must be true")
    if safety.get("raw_secret_handling") != "redact":
        issues.append("safety.raw_secret_handling must be redact")
    if safety.get("private_solution_allowed") is not False:
        issues.append("private_solution_allowed must be false")
    if safety.get("bypass_guidance_allowed") is not False:
        issues.append("bypass_guidance_allowed must be false")

    forbidden_findings = scan_text_files(plugin_dir)
    if forbidden_findings:
        unsafe_blocked = True
        issues.append("forbidden output or private training content detected")

    status = "pass" if not issues else "fail"
    report = {
        "schema_version": "plugin_validation_report/v1",
        "plugin_id": manifest.plugin_id,
        "plugin_type": manifest.type,
        "status": status,
        "risk_level": "high" if high_risk_permissions else "low",
        "high_risk_permissions": sorted(set(high_risk_permissions)),
        "blocking_issues": issues,
        "warnings": warnings,
        "unsafe_plugin_blocked": bool(unsafe_blocked or issues),
        "network_plugin_blocked_by_default": "network_access" in high_risk_permissions or manifest.requires_network,
        "shell_plugin_blocked_by_default": "run_local_command" in high_risk_permissions or manifest.requires_shell,
        "raw_access_plugin_blocked_by_default": "read_raw_evidence" in high_risk_permissions,
        "forbidden_findings": forbidden_findings,
        "external_api_call_count": 0,
        "telemetry_call_count": 0,
        "private_solution_leak_count": 0,
        "forbidden_output_count": 0 if not forbidden_findings else len(forbidden_findings),
        "real_platform_access_count": 0,
    }
    return _write_or_return(plugin_dir, report, write_report)


def _failed(issues: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "plugin_validation_report/v1",
        "plugin_id": None,
        "plugin_type": None,
        "status": "fail",
        "risk_level": "unknown",
        "blocking_issues": issues,
        "warnings": [],
        "unsafe_plugin_blocked": True,
        "external_api_call_count": 0,
        "telemetry_call_count": 0,
        "private_solution_leak_count": 0,
        "forbidden_output_count": 0,
        "real_platform_access_count": 0,
    }


def _write_or_return(plugin_dir: Path, report: dict[str, Any], write_report: bool) -> dict[str, Any]:
    if write_report and plugin_dir.exists():
        (plugin_dir / "plugin_validation_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (plugin_dir / "plugin_validation_report.md").write_text(render_validation_md(report), encoding="utf-8")
    return report


def render_validation_md(report: dict[str, Any]) -> str:
    issues = report.get("blocking_issues", [])
    body = [
        "# Plugin Validation Report",
        "",
        f"- Plugin: `{report.get('plugin_id')}`",
        f"- Type: `{report.get('plugin_type')}`",
        f"- Status: `{report.get('status')}`",
        f"- Risk level: `{report.get('risk_level')}`",
        "",
        "## Blocking Issues",
        "",
    ]
    if issues:
        body.extend(f"- {item}" for item in issues)
    else:
        body.append("- None")
    body.extend(
        [
            "",
            "## Safety",
            "",
            "- Local-only required.",
            "- No external upload.",
            "- Network, shell, raw access, browser profile access, and credential store access are blocked by default.",
            "- Plugin output is candidate-only; core validators remain final authority.",
        ]
    )
    return "\n".join(body) + "\n"
