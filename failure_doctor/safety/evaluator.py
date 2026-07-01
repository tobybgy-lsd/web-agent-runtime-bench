from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ai_handoff_gate import evaluate_ai_handoff
from .audit import audit_manifest
from .cloud_artifact import evaluate_cloud_artifact
from .common import iter_text_files, read_text
from .data_exfiltration import evaluate_data_exfiltration
from .dom_risk import evaluate_dom
from .models import SCHEMA_VERSION, TOOL_VERSION, SafetyFinding
from .patch_gate import evaluate_patch
from .permission_boundary import evaluate_permission_boundary
from .policy import SAFE_NEXT_ACTIONS
from .regulated_workflows import evaluate_regulated_workflow
from .report import write_safety_reports
from .scope import evaluate_scope, safe_project_audit
from .scoring import compliance_score
from .secrets import evaluate_secrets
from .shareability import decide_shareability


def evaluate_safety(
    *,
    project: Path | None = None,
    report: Path | None = None,
    failure_pack: Path | None = None,
    ai_handoff: Path | None = None,
    patch_proposal: Path | None = None,
    cloud_artifact: Path | None = None,
    out_dir: Path,
    allow_broad_scope: bool = False,
) -> dict[str, Any]:
    input_kind, input_path = _select_input(
        project=project,
        report=report,
        failure_pack=failure_pack,
        ai_handoff=ai_handoff,
        patch_proposal=patch_proposal,
        cloud_artifact=cloud_artifact,
    )
    findings: list[SafetyFinding] = []
    findings.extend(evaluate_scope(input_path, allow_broad_scope=allow_broad_scope))
    secret_context = "ai_handoff" if input_kind == "ai_handoff" else "shareable" if input_kind in {"report", "failure_pack"} else "project"
    findings.extend(evaluate_secrets(input_path, context=secret_context))
    findings.extend(evaluate_ai_handoff(input_path if input_kind in {"ai_handoff", "report", "failure_pack"} else None))
    findings.extend(evaluate_patch(input_path if input_kind in {"patch_proposal", "report", "failure_pack"} else None))
    findings.extend(evaluate_dom(input_path))
    findings.extend(evaluate_permission_boundary(input_path))
    findings.extend(evaluate_data_exfiltration(input_path))
    findings.extend(evaluate_cloud_artifact(input_path if input_kind in {"cloud_artifact", "report", "failure_pack"} else None))
    findings.extend(evaluate_regulated_workflow(input_path))
    findings = _renumber(findings)
    text_index = _text_index(input_path)
    shareability = decide_shareability(findings, text_index=text_index)
    score = compliance_score(findings)
    overall_status = _overall_status(findings, shareability["decision"])
    risk_level = _risk_level(findings)
    blocked_actions = sorted({action for finding in findings for action in finding.forbidden_actions})
    audit = safe_project_audit(input_path)
    audit.update(
        audit_manifest(
            input_path,
            input_kind,
            findings,
            "pass" if overall_status == "pass" else overall_status,
        )
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_kind": input_kind,
        "input_path": str(input_path),
        "overall_status": overall_status,
        "risk_level": risk_level,
        "compliance_score": score,
        "shareability": shareability,
        "findings": [finding.to_dict() for finding in findings],
        "blocked_actions": blocked_actions,
        "safe_next_actions": SAFE_NEXT_ACTIONS,
        "audit": audit,
    }
    write_safety_reports(out_dir, payload)
    return payload


def _select_input(**kwargs: Path | None) -> tuple[str, Path]:
    selected = [(name, path) for name, path in kwargs.items() if path is not None]
    if len(selected) != 1:
        raise ValueError("provide exactly one safety input: project, report, failure_pack, ai_handoff, patch_proposal, or cloud_artifact")
    name, path = selected[0]
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"safety input not found: {resolved}")
    return name, resolved


def _renumber(findings: list[SafetyFinding]) -> list[SafetyFinding]:
    for index, finding in enumerate(findings, start=1):
        finding.id = f"finding_{index:03d}"
    return findings


def _text_index(path: Path) -> str:
    parts = [str(path).lower()]
    for item in iter_text_files(path, limit=200):
        parts.append(read_text(item).lower()[:2000])
    return "\n".join(parts)


def _overall_status(findings: list[SafetyFinding], shareability_decision: object) -> str:
    if shareability_decision == "blocked":
        return "blocked"
    if any(finding.severity == "critical" or finding.decision == "block" for finding in findings):
        return "blocked"
    if findings:
        return "warning"
    return "pass"


def _risk_level(findings: list[SafetyFinding]) -> str:
    if any(finding.severity == "critical" for finding in findings):
        return "critical"
    if any(finding.severity == "high" for finding in findings):
        return "high"
    if any(finding.severity == "medium" for finding in findings):
        return "medium"
    if findings:
        return "low"
    return "none"
