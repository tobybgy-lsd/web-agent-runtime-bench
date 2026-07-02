from __future__ import annotations

from .common import FORBIDDEN_TERMS, has_forbidden_text


def evaluate_android_pro_text(text: str) -> dict:
    findings = has_forbidden_text(text)
    return {"status": "pass" if not findings else "fail", "forbidden_terms": findings, "forbidden_output_count": len(findings)}
