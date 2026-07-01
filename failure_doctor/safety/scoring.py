from __future__ import annotations

from .models import SafetyFinding


DIMENSIONS = [
    "scope_safety",
    "secret_safety",
    "shareability",
    "ai_handoff_safety",
    "patch_safety",
    "dom_risk_safety",
    "permission_boundary",
    "data_exfiltration",
    "cloud_artifact_safety",
    "regulated_workflow_safety",
]


def compliance_score(findings: list[SafetyFinding]) -> dict[str, object]:
    scores = {name: 100 for name in DIMENSIONS}
    for finding in findings:
        penalty = 100 if finding.severity == "critical" else 45 if finding.severity == "high" else 20
        key = _dimension_for(finding.type)
        scores[key] = max(0, scores[key] - penalty)
    overall = min(scores.values()) if scores else 100
    if any(f.severity == "critical" for f in findings):
        overall = 0
    elif any(f.severity == "high" for f in findings):
        overall = min(overall, 70)
    return {
        "overall_score": overall,
        "dimensions": scores,
        "status": "pass" if overall >= 95 else "blocked" if overall < 70 else "warning",
    }


def _dimension_for(kind: str) -> str:
    return {
        "scope_violation": "scope_safety",
        "secret_leak": "secret_safety",
        "unsafe_handoff": "ai_handoff_safety",
        "unsafe_patch": "patch_safety",
        "malicious_dom": "dom_risk_safety",
        "permission_boundary": "permission_boundary",
        "data_exfiltration": "data_exfiltration",
        "cloud_artifact_risk": "cloud_artifact_safety",
        "regulated_workflow_risk": "regulated_workflow_safety",
    }.get(kind, "shareability")
