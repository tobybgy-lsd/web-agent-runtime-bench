from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from .common import iter_text_files
from .models import SafetyFinding, TOOL_VERSION


def audit_manifest(input_path: Path, input_kind: str, findings: list[SafetyFinding], decision: str) -> dict[str, object]:
    files_scanned = sum(1 for _ in iter_text_files(input_path)) if input_path.exists() else 0
    return {
        "tool_version": TOOL_VERSION,
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path),
        "input_kind": input_kind,
        "local_only": True,
        "no_upload": True,
        "files_scanned": files_scanned,
        "files_blocked": sum(1 for finding in findings if finding.decision == "block"),
        "findings_count": len(findings),
        "critical_count": sum(1 for finding in findings if finding.severity == "critical"),
        "high_count": sum(1 for finding in findings if finding.severity == "high"),
        "decision": decision,
        "safe_outputs": ["safety_evaluation_report.md", "open_this_first_safety.md"],
        "blocked_outputs": ["raw artifacts"] if decision != "pass" else [],
    }
