"""Candidate collection for composite diagnosis."""

from __future__ import annotations

import json
from typing import Any, Mapping

from . import classifier
from .evidence_nodes import extract_evidence_nodes


def collect_diagnosis_candidates(artifact: Mapping[str, Any]) -> list[dict[str, Any]]:
    nodes = extract_evidence_nodes(artifact)
    text = json.dumps(artifact, ensure_ascii=False).lower()
    raw_results = []
    for classify in classifier.CLASSIFIERS:
        result = classify(artifact, text)
        if result:
            raw_results.append(result)

    by_type: dict[str, dict[str, Any]] = {}
    for result in raw_results:
        _add_candidate(by_type, result, nodes)

    for category in sorted({support for node in nodes for support in node.get("supports", [])}):
        if category in {"auth_or_permission_block"}:
            category = "anti_bot_risk"
        if category not in by_type:
            _add_candidate(
                by_type,
                {
                    "failure_type": category,
                    "subtype": _subtype_from_nodes(category, nodes),
                    "confidence": _confidence_from_nodes(category, nodes),
                    "evidence": [node["label"] for node in nodes if category in node.get("supports", [])],
                    "suggested_fix": _generic_fix(category),
                    "safe_next_action": True,
                },
                nodes,
            )

    if not by_type or (_only_weak_user_evidence(nodes) and not raw_results):
        by_type = {}
        _add_candidate(
            by_type,
            {
                "failure_type": "insufficient_evidence",
                "subtype": "structured_evidence_missing",
                "confidence": 0.45,
                "evidence": ["only weak or insufficient structured evidence is available"],
                "suggested_fix": ["collect error.log, network.json, trace.zip, or a minimal reproduction before editing code"],
                "safe_next_action": True,
            },
            nodes,
        )

    candidates = list(by_type.values())
    candidates.sort(key=lambda item: (item["blocking_priority"], item["score"], item["confidence"]), reverse=True)
    for index, candidate in enumerate(candidates, start=1):
        candidate["candidate_id"] = f"C{index}"
    return candidates


def _add_candidate(target: dict[str, dict[str, Any]], result: Mapping[str, Any], nodes: list[Mapping[str, Any]]) -> None:
    technical = str(result.get("failure_type") or result.get("technical_category") or "unknown")
    evidence_ids = [node["id"] for node in nodes if technical in node.get("supports", [])]
    if not evidence_ids and technical == "selector_drift":
        evidence_ids = [node["id"] for node in nodes if "selector" in str(node.get("label", "")).lower()]
    if not evidence_ids:
        evidence_ids = [nodes[0]["id"]] if nodes else []
    score = _score_candidate(technical, result, nodes, evidence_ids)
    existing = target.get(technical)
    candidate = {
        "candidate_id": "",
        "failure_layer": _failure_layer_for(technical),
        "technical_category": technical,
        "failure_type": technical,
        "subtype": result.get("subtype"),
        "confidence": float(result.get("confidence") or 0.0),
        "score": score,
        "evidence_ids": evidence_ids,
        "positive_evidence": list(result.get("evidence", [])) if isinstance(result.get("evidence", []), list) else [],
        "negative_evidence": [],
        "candidate_source": str(result.get("candidate_source") or technical),
        "blocking_priority": _blocking_priority(technical),
        "downstream_likelihood": _downstream_likelihood(technical),
        "safe_next_action": True,
    }
    if technical == "anti_bot_risk":
        candidate["safe_next_action"] = True
    if existing is None or candidate["score"] > existing["score"]:
        target[technical] = candidate


def _score_candidate(technical: str, result: Mapping[str, Any], nodes: list[Mapping[str, Any]], evidence_ids: list[str]) -> float:
    severity_score = 0.0
    for node in nodes:
        if node["id"] not in evidence_ids:
            continue
        severity_score += {"high": 5.0, "medium": 3.0, "low": 1.0}.get(str(node.get("severity")), 1.0)
    return round(severity_score + float(result.get("confidence") or 0) * 4 + _blocking_priority(technical), 2)


def _blocking_priority(technical: str) -> int:
    if technical in {"anti_bot_risk", "network_http_error", "toolchain_environment"}:
        return 9
    if technical in {"playwright_storage_state_context", "auth_expiry"}:
        return 8
    if technical in {"playwright_route_mock_har"}:
        return 7
    if technical in {"playwright_execution_context_destroyed", "playwright_browser_context_closed", "cdp_websocket_disconnected"}:
        return 6
    if technical in {"playwright_shadow_dom_locator", "playwright_frame_locator", "playwright_popup", "playwright_file_chooser", "playwright_download", "website_change"}:
        return 5
    if technical in {"response_shape_change"}:
        return 4
    if technical == "insufficient_evidence":
        return 1
    return 3


def _downstream_likelihood(technical: str) -> int:
    if technical in {"selector_drift", "response_shape_change", "async_hydration_timing"}:
        return 8
    if technical in {"network_http_error"}:
        return 4
    return 2


def _failure_layer_for(technical: str) -> str:
    if technical == "anti_bot_risk":
        return "anti_bot_risk"
    if technical in {"network_http_error", "toolchain_environment", "cdp_websocket_disconnected"}:
        return "environment"
    if technical in {"website_change", "response_shape_change"}:
        return "website_change"
    if technical == "insufficient_evidence":
        return "insufficient_evidence"
    return "automation_engineering"


def _subtype_from_nodes(category: str, nodes: list[Mapping[str, Any]]) -> str:
    labels = " ".join(str(node.get("label", "")).lower() for node in nodes if category in node.get("supports", []))
    if category == "anti_bot_risk" and "429" in labels:
        return "rate_limited"
    if category == "playwright_storage_state_context":
        return "login_redirect_after_authenticated_action"
    if category == "playwright_route_mock_har":
        return "har_not_found_or_not_loaded"
    if category == "network_http_error" and "404" in labels:
        return "http_404"
    return "inferred"


def _confidence_from_nodes(category: str, nodes: list[Mapping[str, Any]]) -> float:
    severities = [str(node.get("severity")) for node in nodes if category in node.get("supports", [])]
    if "high" in severities:
        return 0.9
    if "medium" in severities:
        return 0.72
    return 0.45


def _generic_fix(category: str) -> list[str]:
    fixes = {
        "playwright_storage_state_context": ["fix authenticated context before debugging downstream selectors"],
        "selector_drift": ["inspect the current DOM after blockers are resolved"],
        "playwright_route_mock_har": ["register route/HAR mocks before the first matching request"],
        "network_http_error": ["fix transport or endpoint availability before changing parsing logic"],
        "anti_bot_risk": ["use an authorized/compliant access path or stop automation if authorization is unclear"],
        "website_change": ["update selectors, endpoints, or schema mapping from fresh evidence"],
    }
    return fixes.get(category, ["collect more structured evidence and make the smallest safe fix"])


def _only_weak_user_evidence(nodes: list[Mapping[str, Any]]) -> bool:
    return bool(nodes) and all(node.get("type") == "user_description" for node in nodes)
