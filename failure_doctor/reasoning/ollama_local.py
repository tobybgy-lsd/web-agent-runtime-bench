from __future__ import annotations

from typing import Any


def reason(bundle: dict[str, Any], *, model: str | None = None, endpoint: str = "http://127.0.0.1:11434") -> dict[str, Any]:
    return {
        "provider": "ollama_local",
        "provider_status": "provider_unavailable",
        "reason": "Local Ollama reasoning is optional and was not contacted by default.",
        "model": model,
        "endpoint": endpoint,
        "claims": [],
        "hypotheses": [],
        "causal_chain": {"chain_id": "C001", "nodes": [], "edges": [], "root_cause_node_id": None},
        "root_cause_graph": {"graph_id": "RCG001", "primary_root_cause": None, "secondary_contributors": [], "downstream_symptoms": [], "rejected_causes": [], "verification_plan": []},
        "competing_hypotheses": [],
        "external_api_call_count": 0,
        "model_download_count": 0,
    }
