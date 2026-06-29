from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


def create_regression_case(before_input: str, after_input: str, verification_report: Mapping[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    before = verification_report.get("before", {})
    after = verification_report.get("after", {})
    evidence = list(verification_report.get("remaining_evidence", [])) + list(verification_report.get("resolved_evidence", []))
    return {
        "case_id": f"REG-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}",
        "source": "verification_loop",
        "before_input": before_input,
        "after_input": after_input,
        "before_failure_type": before.get("failure_type", "unknown") if isinstance(before, Mapping) else "unknown",
        "before_subtype": before.get("subtype", "") if isinstance(before, Mapping) else "",
        "verification_status": verification_report.get("status", "insufficient_evidence"),
        "expected_future_diagnosis": after.get("failure_type", "none_detected") if isinstance(after, Mapping) else "none_detected",
        "evidence_to_watch": [str(item) for item in evidence[:10]],
        "created_at": now.isoformat(),
        "safe_to_publish": False,
    }
