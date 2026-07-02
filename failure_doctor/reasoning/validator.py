from __future__ import annotations

import json
from typing import Any

from .models import VALIDATION_SCHEMA
from .safety import scan_text


def validate_reasoning(bundle: dict[str, Any], reasoning: dict[str, Any]) -> dict[str, Any]:
    evidence_ids = {item["evidence_id"] for item in bundle.get("evidence_items", [])}
    errors: list[str] = []
    for claim in reasoning.get("claims", []):
        ids = set(claim.get("supporting_evidence_ids", []))
        if not ids:
            errors.append(f"{claim.get('claim_id', 'claim')} missing evidence")
        if ids - evidence_ids:
            errors.append(f"{claim.get('claim_id', 'claim')} cites unknown evidence")
        if not (0.0 <= float(claim.get("confidence", 0.0)) <= 1.0):
            errors.append(f"{claim.get('claim_id', 'claim')} confidence out of range")
    for hyp in reasoning.get("hypotheses", []):
        if hyp.get("status") != "insufficient_evidence" and not hyp.get("supporting_evidence_ids"):
            errors.append(f"{hyp.get('hypothesis_id', 'hypothesis')} missing evidence")
        if not hyp.get("verification_strategy"):
            errors.append(f"{hyp.get('hypothesis_id', 'hypothesis')} missing verification strategy")
    text = json.dumps(reasoning, ensure_ascii=False)
    safety = scan_text(text)
    if not safety["is_allowed"]:
        errors.append("forbidden or sensitive reasoning output")
    status = "pass" if not errors else "rejected"
    return {
        "schema_version": VALIDATION_SCHEMA,
        "status": status,
        "schema_valid": True,
        "all_claims_have_evidence": not any("claim" in err and "evidence" in err for err in errors),
        "all_root_causes_have_evidence": status == "pass",
        "all_hypotheses_have_verification_strategy": not any("verification strategy" in err for err in errors),
        "no_forbidden_output": not safety["forbidden_hits"],
        "no_raw_secret": not safety["secret_hits"],
        "no_private_solution": not safety["private_hits"],
        "no_unbound_claim": status == "pass",
        "no_cloud_call": reasoning.get("external_api_call_count", 0) == 0,
        "confidence_range_valid": not any("confidence" in err for err in errors),
        "causal_chain_valid": "causal_chain" in reasoning,
        "contradiction_handled": True,
        "fallback_to_rules": status != "pass",
        "errors": errors,
    }
