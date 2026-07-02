from __future__ import annotations

from typing import Any


def reason(bundle: dict[str, Any]) -> dict[str, Any]:
    items = bundle.get("evidence_items", [])
    if not items:
        return _insufficient()
    primary = items[0]
    evidence_id = primary["evidence_id"]
    title = _title(primary.get("summary", ""))
    claim = {
        "claim_id": "claim_001",
        "claim_type": "root_cause",
        "text": title,
        "confidence": float(primary.get("confidence", 0.75)),
        "supporting_evidence_ids": [evidence_id],
        "contradicting_evidence_ids": [],
        "is_evidence_bound": True,
        "is_allowed": True,
        "safety_flags": [],
    }
    hypothesis = {
        "hypothesis_id": "H001",
        "title": title,
        "status": "supported",
        "confidence": claim["confidence"],
        "supporting_evidence_ids": [evidence_id],
        "contradicting_evidence_ids": [],
        "verification_strategy": [
            "Re-run the failing workflow after the smallest scoped fix.",
            "Compare before/after sanitized evidence and keep the regression case.",
        ],
        "safe_next_action": ["Use the deterministic diagnosis and evidence-bound fix plan first."],
    }
    chain = {
        "chain_id": "C001",
        "nodes": [
            {
                "node_id": "N001",
                "event": title,
                "evidence_ids": [evidence_id],
                "confidence": claim["confidence"],
            }
        ],
        "edges": [],
        "root_cause_node_id": "N001",
    }
    graph = {
        "graph_id": "RCG001",
        "primary_root_cause": {
            "node_id": "N001",
            "label": title,
            "confidence": claim["confidence"],
            "evidence_ids": [evidence_id],
        },
        "secondary_contributors": [],
        "downstream_symptoms": [],
        "rejected_causes": [],
        "verification_plan": hypothesis["verification_strategy"],
    }
    return {
        "provider": "mock_reasoner",
        "provider_status": "available",
        "claims": [claim],
        "hypotheses": [hypothesis],
        "causal_chain": chain,
        "root_cause_graph": graph,
        "competing_hypotheses": [hypothesis],
        "external_api_call_count": 0,
        "model_download_count": 0,
    }


def _insufficient() -> dict[str, Any]:
    return {
        "provider": "mock_reasoner",
        "provider_status": "available",
        "claims": [],
        "hypotheses": [
            {
                "hypothesis_id": "H001",
                "title": "insufficient_evidence",
                "status": "insufficient_evidence",
                "confidence": 0.0,
                "supporting_evidence_ids": [],
                "contradicting_evidence_ids": [],
                "verification_strategy": ["Collect a sanitized diagnosis report with evidence.json."],
                "safe_next_action": ["Provide more local sanitized evidence."],
            }
        ],
        "causal_chain": {"chain_id": "C001", "nodes": [], "edges": [], "root_cause_node_id": None},
        "root_cause_graph": {
            "graph_id": "RCG001",
            "primary_root_cause": None,
            "secondary_contributors": [],
            "downstream_symptoms": [],
            "rejected_causes": [],
            "verification_plan": ["Collect more evidence."],
        },
        "competing_hypotheses": [],
        "external_api_call_count": 0,
        "model_download_count": 0,
    }


def _title(summary: str) -> str:
    lower = summary.lower()
    if "proxy" in lower or "network" in lower:
        return "network/proxy evidence likely caused downstream automation failure"
    if "login" in lower or "auth" in lower:
        return "auth/session evidence likely caused redirect and missing target state"
    if "ocr" in lower:
        return "OCR evidence likely contributed to wrong field extraction"
    if "visual" in lower or "coordinate" in lower:
        return "visual runtime evidence likely caused wrong action targeting"
    if "schema" in lower or "duplicate" in lower or "pagination" in lower:
        return "data quality evidence likely caused downstream validation failure"
    return "primary failure is supported by the strongest sanitized evidence item"
