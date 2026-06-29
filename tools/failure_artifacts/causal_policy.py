"""Causal policy for ranking composite diagnosis candidates."""

from __future__ import annotations

from typing import Any, Mapping


def determine_primary_failure(candidates: list[Mapping[str, Any]], graph: Mapping[str, Any]) -> dict[str, Any]:
    if not candidates:
        return _insufficient_candidate()
    blocked = {edge.get("to") for edge in graph.get("edges", []) if edge.get("relation") in {"blocks", "likely_causes"} and float(edge.get("confidence", 0)) >= 0.6}
    ranked = sorted(candidates, key=lambda item: (item.get("blocking_priority", 0), item.get("score", 0), item.get("confidence", 0)), reverse=True)
    for candidate in ranked:
        if set(candidate.get("evidence_ids", [])) & set(blocked):
            continue
        return dict(candidate)
    return dict(ranked[0])


def determine_secondary_failures(candidates: list[Mapping[str, Any]], graph: Mapping[str, Any], primary: Mapping[str, Any]) -> list[dict[str, Any]]:
    primary_type = primary.get("technical_category")
    secondary = []
    for candidate in candidates:
        if candidate.get("technical_category") == primary_type:
            continue
        relationship = _relationship(candidate, graph)
        item = dict(candidate)
        if _should_suppress_downstream(primary, item):
            relationship = "suppressed_downstream"
            item["suppressed_by_primary"] = True
            item["suppression_reason"] = (
                "anti_bot_risk is a blocking access layer; inspect this downstream symptom only after a compliant access path succeeds"
            )
        item["relationship_to_primary"] = relationship
        secondary.append(item)
    return secondary


def determine_blocking_failure(primary: Mapping[str, Any], secondary: list[Mapping[str, Any]], graph: Mapping[str, Any]) -> dict[str, Any]:
    technical = str(primary.get("technical_category") or "insufficient_evidence")
    return {
        "technical_category": technical,
        "subtype": str(primary.get("subtype") or ""),
        "reason": _blocking_reason(technical, graph),
        "evidence_ids": list(primary.get("evidence_ids", [])),
    }


def identify_downstream_failures(primary: Mapping[str, Any], secondary: list[Mapping[str, Any]], graph: Mapping[str, Any]) -> list[dict[str, Any]]:
    downstream = []
    for item in secondary:
        if item.get("relationship_to_primary") in {"downstream", "blocked_by_primary", "suppressed_downstream"} or item.get("downstream_likelihood", 0) >= 5:
            downstream.append(
                {
                    "technical_category": item.get("technical_category"),
                    "subtype": item.get("subtype"),
                    "caused_by": primary.get("technical_category"),
                    "evidence_ids": list(item.get("evidence_ids", [])),
                    "suppressed_by_primary": bool(item.get("suppressed_by_primary")),
                }
            )
    return downstream


def build_repair_order(primary: Mapping[str, Any], secondary: list[Mapping[str, Any]], graph: Mapping[str, Any]) -> list[str]:
    technical = str(primary.get("technical_category") or "insufficient_evidence")
    if technical == "anti_bot_risk":
        return [
            "Confirm authorization and use an official API, authorized export, manual review, or stop automation if access is unclear.",
            "Only after the compliant path is confirmed, re-run to see whether downstream selectors or parsing still fail.",
        ]
    if technical in {"network_http_error", "toolchain_environment", "cdp_websocket_disconnected"}:
        return ["Fix the network/runtime/environment blocker first.", "Re-run the automation before changing selectors or parsers."]
    if technical in {"playwright_storage_state_context", "auth_expiry"}:
        return ["Restore authenticated context or session state first.", "Re-run and inspect selector or data-shape symptoms only after auth succeeds."]
    if technical == "playwright_route_mock_har":
        return ["Fix route/HAR/mock registration before the first matching request.", "Then validate response shape and parser behavior."]
    if technical in {"playwright_shadow_dom_locator", "playwright_frame_locator", "playwright_popup"}:
        return ["Fix the DOM/frame/page targeting strategy first.", "Then check whether selectors still need updating."]
    if technical == "website_change":
        return ["Update the changed endpoint, schema, or DOM contract first.", "Then repair downstream parsing or business mapping."]
    return ["Collect stronger structured evidence before editing code."]


def _relationship(candidate: Mapping[str, Any], graph: Mapping[str, Any]) -> str:
    evidence_ids = set(candidate.get("evidence_ids", []))
    for edge in graph.get("edges", []):
        if edge.get("to") in evidence_ids and edge.get("relation") in {"blocks", "likely_causes"}:
            return "blocked_by_primary" if edge.get("relation") == "blocks" else "downstream"
        if edge.get("relation") == "competes_with" and (edge.get("from") in evidence_ids or edge.get("to") in evidence_ids):
            return "competing"
    return "sibling"


def _should_suppress_downstream(primary: Mapping[str, Any], candidate: Mapping[str, Any]) -> bool:
    if primary.get("technical_category") != "anti_bot_risk":
        return False
    technical = str(candidate.get("technical_category") or "")
    if int(candidate.get("downstream_likelihood") or 0) >= 5:
        return True
    return technical in {
        "selector_drift",
        "website_change",
        "response_shape_change",
        "async_hydration_timing",
        "playwright_shadow_dom_locator",
        "playwright_frame_locator",
    }


def _blocking_reason(technical: str, graph: Mapping[str, Any]) -> str:
    reasons = [str(edge.get("reason")) for edge in graph.get("edges", []) if edge.get("relation") in {"blocks", "likely_causes"}]
    if reasons:
        return reasons[0]
    return f"{technical} has the strongest structured evidence and priority score"


def _insufficient_candidate() -> dict[str, Any]:
    return {
        "candidate_id": "C1",
        "failure_layer": "insufficient_evidence",
        "technical_category": "insufficient_evidence",
        "failure_type": "insufficient_evidence",
        "subtype": "structured_evidence_missing",
        "confidence": 0.45,
        "score": 1,
        "evidence_ids": [],
        "positive_evidence": ["insufficient structured evidence"],
        "negative_evidence": [],
        "candidate_source": "causal_policy",
        "blocking_priority": 1,
        "downstream_likelihood": 0,
        "safe_next_action": True,
    }
