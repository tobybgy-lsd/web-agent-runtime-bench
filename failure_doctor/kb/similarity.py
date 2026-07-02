from __future__ import annotations

from typing import Any

from .fingerprint import fingerprint_from_payload, normalize_tokens
from .redaction import stable_text


def match_case(report_payload: dict[str, Any], case_payload: dict[str, Any]) -> dict[str, Any]:
    report_fp = fingerprint_from_payload(report_payload)
    case_fp = case_payload.get("evidence_fingerprint") or fingerprint_from_payload(case_payload)
    matched: list[str] = []
    score = 0.0
    weights = {
        "failure_type": 0.24,
        "subtype": 0.28,
        "framework": 0.08,
        "domain": 0.05,
        "primary_fingerprint": 0.15,
        "context_signature": 0.05,
    }
    for field, weight in weights.items():
        if report_fp.get(field) and report_fp.get(field) == case_fp.get(field):
            score += weight
            matched.append(field)
    report_tokens = set(report_fp.get("tokens", []))
    case_tokens = set(case_fp.get("tokens", []))
    if report_tokens or case_tokens:
        overlap = len(report_tokens & case_tokens) / max(1, len(report_tokens | case_tokens))
        score += min(0.25, overlap * 0.5)
        if overlap:
            matched.append("normalized_error_token_overlap")
    score = min(1.0, round(score, 3))
    return {
        "case_id": case_payload.get("case_id"),
        "score": score,
        "failure_type": case_payload.get("failure_type"),
        "subtype": case_payload.get("subtype"),
        "verified_fix_available": case_payload.get("fix_status") == "verified",
        "matched_dimensions": matched,
        "why_matched": f"Matched {', '.join(matched) or 'no strong dimensions'} with local-only fingerprints.",
        "why_not_exact": "Similarity is evidence-based and must be verified before reuse.",
    }


def search_score(query: str, case_payload: dict[str, Any]) -> float:
    query_tokens = set(normalize_tokens(query))
    case_tokens = set(normalize_tokens(stable_text(case_payload)))
    if not query_tokens:
        return 0.0
    return round(len(query_tokens & case_tokens) / max(1, len(query_tokens)), 3)
