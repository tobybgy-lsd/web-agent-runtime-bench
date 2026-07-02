from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PLUGIN_SCHEMA_VERSION = "failure_doctor_plugin/v1"
PLUGIN_TYPES = {
    "framework-adapter",
    "evidence-adapter",
    "diagnosis-rule",
    "industry-pack",
    "console-extension",
    "ci-extension",
    "kb-pattern",
    "reasoning-tool",
    "report-exporter",
    "validation-pack",
}

SAFE_DEFAULT_PERMISSIONS = {
    "read_input_dir",
    "write_output_dir",
    "emit_evidence",
}

ALL_PERMISSIONS = SAFE_DEFAULT_PERMISSIONS | {
    "read_report_summary",
    "read_sanitized_evidence",
    "read_raw_evidence",
    "emit_diagnosis_candidate",
    "emit_fix_candidate",
    "emit_console_page",
    "emit_ci_summary",
    "emit_kb_pattern",
    "emit_reasoning_tool",
    "emit_report_export",
    "run_local_command",
    "network_access",
    "write_project_files",
    "read_kb_summary",
    "write_kb_candidate",
}

HIGH_RISK_PERMISSIONS = {
    "read_raw_evidence",
    "run_local_command",
    "network_access",
    "write_project_files",
}

FORBIDDEN_PERMISSIONS = {
    "read_browser_profile",
    "read_credential_store",
    "disable_safety_gate",
}

HOOKS = {
    "collect.adapter",
    "collect.postprocess",
    "diagnose.preprocess",
    "diagnose.rule_candidate",
    "diagnose.postprocess",
    "evidence.normalize",
    "safety.precheck",
    "safety.postcheck",
    "handoff.enrich",
    "patch.proposal_review",
    "verify.postprocess",
    "kb.fingerprint",
    "kb.similarity",
    "ci.summary_section",
    "console.page",
    "reasoning.tool",
    "report.exporter",
    "validation.case_provider",
}

DEFAULT_HOOKS_BY_TYPE = {
    "framework-adapter": ["collect.adapter", "diagnose.preprocess"],
    "evidence-adapter": ["evidence.normalize"],
    "diagnosis-rule": ["diagnose.rule_candidate"],
    "industry-pack": ["diagnose.rule_candidate", "validation.case_provider"],
    "console-extension": ["console.page"],
    "ci-extension": ["ci.summary_section"],
    "kb-pattern": ["kb.fingerprint", "kb.similarity"],
    "reasoning-tool": ["reasoning.tool"],
    "report-exporter": ["report.exporter"],
    "validation-pack": ["validation.case_provider"],
}


@dataclass(frozen=True)
class PluginManifest:
    schema_version: str
    plugin_id: str
    name: str
    version: str
    type: str
    entrypoint: str
    description: str
    local_only: bool
    no_upload: bool
    no_external_api: bool
    requires_network: bool
    requires_shell: bool
    requires_write_access: bool
    permissions: tuple[str, ...]
    hooks: tuple[str, ...]
    safety: dict[str, Any]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "PluginManifest":
        return cls(
            schema_version=str(payload.get("schema_version", "")),
            plugin_id=str(payload.get("plugin_id", "")),
            name=str(payload.get("name", "")),
            version=str(payload.get("version", "")),
            type=str(payload.get("type", "")),
            entrypoint=str(payload.get("entrypoint", "")),
            description=str(payload.get("description", "")),
            local_only=bool(payload.get("local_only", False)),
            no_upload=bool(payload.get("no_upload", False)),
            no_external_api=bool(payload.get("no_external_api", False)),
            requires_network=bool(payload.get("requires_network", False)),
            requires_shell=bool(payload.get("requires_shell", False)),
            requires_write_access=bool(payload.get("requires_write_access", False)),
            permissions=tuple(str(item) for item in payload.get("permissions", [])),
            hooks=tuple(str(item) for item in payload.get("hooks", [])),
            safety=dict(payload.get("safety", {})),
        )
