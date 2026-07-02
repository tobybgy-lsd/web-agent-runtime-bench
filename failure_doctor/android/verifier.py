from __future__ import annotations

from typing import Any


def verify_step_expectation(step: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    expected_text = (step.get("verify") or {}).get("text_exists")
    if not expected_text:
        return {"status": "pass", "reason": "no_text_expectation"}
    texts = " ".join(str(node.get("text", "")) for node in evidence.get("nodes", []))
    return {"status": "pass" if expected_text in texts else "fail", "expected_text": expected_text}
