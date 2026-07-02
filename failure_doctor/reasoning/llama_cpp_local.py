from __future__ import annotations

from pathlib import Path
from typing import Any


def reason(bundle: dict[str, Any], *, model_path: str | None = None) -> dict[str, Any]:
    available = bool(model_path and Path(model_path).exists())
    return {
        "provider": "llama_cpp_local",
        "provider_status": "provider_unavailable" if not available else "not_invoked",
        "reason": "Local llama.cpp reasoning is optional; no model is downloaded or required.",
        "model_path": model_path,
        "claims": [],
        "hypotheses": [],
        "causal_chain": {"chain_id": "C001", "nodes": [], "edges": [], "root_cause_node_id": None},
        "root_cause_graph": {"graph_id": "RCG001", "primary_root_cause": None, "secondary_contributors": [], "downstream_symptoms": [], "rejected_causes": [], "verification_plan": []},
        "competing_hypotheses": [],
        "external_api_call_count": 0,
        "model_download_count": 0,
    }
