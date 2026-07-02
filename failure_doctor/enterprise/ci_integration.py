from __future__ import annotations

import json
from pathlib import Path

from .audit import append_audit
from .workspace import validate_workspace


def attach_enterprise_ci(out: Path, enterprise_workspace: Path) -> dict:
    status = validate_workspace(enterprise_workspace)
    audit_ref = append_audit(
        enterprise_workspace,
        actor="ci",
        action="ci.diagnose",
        target=str(out),
        decision="pass" if status.get("status") == "pass" else "fail",
    )
    summary = {
        "schema_version": "enterprise_ci_summary/v1",
        "enterprise_policy": "active",
        "gate_policy": status.get("status"),
        "approval_required": False,
        "enterprise_audit_ref": audit_ref,
        "sanitized_artifact_only": True,
        "external_api_call_count": 0,
        "telemetry_call_count": 0,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "enterprise_ci_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary_md = out / "ci_summary.md"
    if summary_md.exists():
        with summary_md.open("a", encoding="utf-8") as handle:
            handle.write("\n## Enterprise Governance\n\n")
            handle.write("- Enterprise policy: active\n")
            handle.write(f"- Gate policy: {summary['gate_policy']}\n")
            handle.write(f"- Audit ref: `{audit_ref}`\n")
    return summary
