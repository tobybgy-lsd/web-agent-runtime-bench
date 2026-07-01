from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_safety_reports(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "safety_evaluation_report.json", payload)
    (out_dir / "safety_evaluation_report.md").write_text(render_markdown(payload), encoding="utf-8")
    _write_json(out_dir / "blocked_actions.json", {"blocked_actions": payload.get("blocked_actions", [])})
    _write_json(
        out_dir / "sensitive_data_findings.json",
        {"findings": [f for f in payload.get("findings", []) if f.get("type") == "secret_leak"]},
    )
    _write_json(out_dir / "ai_handoff_safety.json", _filter(payload, "unsafe_handoff"))
    _write_json(out_dir / "shareability_decision.json", payload.get("shareability", {}))
    _write_json(out_dir / "dom_risk_report.json", _filter(payload, "malicious_dom"))
    _write_json(out_dir / "permission_boundary_report.json", _filter(payload, "permission_boundary"))
    _write_json(out_dir / "data_exfiltration_report.json", _filter(payload, "data_exfiltration"))
    _write_json(out_dir / "cloud_artifact_safety.json", _filter(payload, "cloud_artifact_risk"))
    _write_json(out_dir / "regulated_workflow_safety.json", _filter(payload, "regulated_workflow_risk"))
    _write_json(out_dir / "patch_safety_report.json", _filter(payload, "unsafe_patch"))
    _write_json(out_dir / "compliance_score.json", payload.get("compliance_score", {}))
    _write_json(out_dir / "safety_audit_manifest.json", payload.get("audit", {}))
    (out_dir / "open_this_first_safety.md").write_text(render_open_first(payload), encoding="utf-8")


def render_markdown(payload: dict[str, Any]) -> str:
    findings = payload.get("findings", [])
    lines = [
        "# Safety Evaluation Report",
        "",
        f"- Status: `{payload.get('overall_status')}`",
        f"- Risk level: `{payload.get('risk_level')}`",
        f"- Shareability: `{payload.get('shareability', {}).get('decision')}`",
        f"- Compliance score: `{payload.get('compliance_score', {}).get('overall_score')}`",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("No safety findings were detected in the provided local input.")
    for finding in findings:
        lines.extend(
            [
                f"### {finding.get('id')} `{finding.get('type')}`",
                "",
                f"- Severity: `{finding.get('severity')}`",
                f"- Decision: `{finding.get('decision')}`",
                f"- Safe next action: {finding.get('safe_next_action')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Safety Boundary",
            "",
            "Local-only. No upload. No active probe. No bypass, evasion, spoofing, cracking, challenge automation, or private remediation guidance.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_open_first(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Open This First - Safety",
            "",
            f"- Safety evaluation status: `{payload.get('overall_status')}`",
            f"- Risk level: `{payload.get('risk_level')}`",
            f"- Shareability decision: `{payload.get('shareability', {}).get('decision')}`",
            f"- Blocked outputs: `{', '.join(payload.get('shareability', {}).get('blocked_outputs', [])) or 'none'}`",
            f"- Safe outputs: `{', '.join(payload.get('shareability', {}).get('allowed_outputs', [])) or 'none'}`",
            "",
            "If this report is blocked, stop and perform manual review before sharing artifacts or giving them to an AI agent.",
        ]
    ) + "\n"


def _filter(payload: dict[str, Any], kind: str) -> dict[str, Any]:
    return {"findings": [finding for finding in payload.get("findings", []) if finding.get("type") == kind]}


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
