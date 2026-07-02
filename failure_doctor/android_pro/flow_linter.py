from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import has_forbidden_text, is_final_action_text, read_flow, write_json


def lint_flow_file(flow: Path, profile: Path | None = None, out: Path | None = None) -> dict[str, Any]:
    payload = read_flow(flow)
    findings: list[dict[str, Any]] = []
    if payload.get("authorized_target") is not True:
        findings.append({"severity": "critical", "code": "authorized_target_required"})
    if payload.get("allow_final_submit") is True:
        findings.append({"severity": "critical", "code": "allow_final_submit_forbidden_by_default"})
    if payload.get("target_kind") in {None, "unknown"}:
        findings.append({"severity": "high", "code": "target_kind_missing"})
    for term in has_forbidden_text(str(payload)):
        findings.append({"severity": "critical", "code": "forbidden_flow_term", "term": term})
    for idx, step in enumerate(payload.get("steps", [])):
        if step.get("strategy") == "coordinate" or "coordinate" in str(step.get("locator", "")).lower():
            findings.append({"severity": "critical", "code": "absolute_coordinate_blocked", "step": idx})
        if is_final_action_text(str(step.get("text") or step.get("value") or step.get("action"))):
            findings.append({"severity": "critical", "code": "publish_guard_blocked", "step": idx})
    status = "fail" if any(f["severity"] == "critical" for f in findings) else "pass"
    report = {"schema_version": "android_flow_lint/v1", "status": status, "findings": findings, "step_count": len(payload.get("steps", []))}
    if out:
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "flow_lint_report.json", report)
    return report
