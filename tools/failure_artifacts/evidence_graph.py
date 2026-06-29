"""Evidence graph construction for composite diagnosis."""

from __future__ import annotations

from typing import Any, Mapping


def build_evidence_graph(nodes: list[Mapping[str, Any]], candidates: list[Mapping[str, Any]]) -> dict[str, Any]:
    graph_nodes = [dict(node) for node in nodes]
    edges: list[dict[str, Any]] = []

    def node_for(category: str) -> Mapping[str, Any] | None:
        for node in nodes:
            if category in node.get("supports", []):
                return node
        return None

    def add_edge(source_category: str, target_category: str, relation: str, reason: str, confidence: float = 0.84) -> None:
        source = node_for(source_category)
        target = node_for(target_category)
        if not source or not target or source["id"] == target["id"]:
            return
        edges.append(
            {
                "from": source["id"],
                "to": target["id"],
                "relation": relation,
                "confidence": confidence,
                "reason": reason,
            }
        )

    categories = {str(candidate.get("technical_category")) for candidate in candidates}
    if {"playwright_storage_state_context", "selector_drift"} <= categories or {"auth_expiry", "selector_drift"} <= categories:
        add_edge("playwright_storage_state_context", "selector_drift", "blocks", "auth redirect/login evidence blocks downstream selector diagnosis", 0.9)
        add_edge("auth_expiry", "selector_drift", "blocks", "auth/session evidence blocks downstream selector diagnosis", 0.88)
    if {"anti_bot_risk", "selector_drift"} <= categories:
        add_edge("anti_bot_risk", "selector_drift", "blocks", "access-control boundary blocks downstream page selectors", 0.92)
    if {"anti_bot_risk", "network_http_error"} <= categories:
        add_edge("anti_bot_risk", "network_http_error", "blocks", "access/rate boundary explains downstream network symptoms", 0.82)
    if {"playwright_route_mock_har", "network_http_error"} <= categories:
        add_edge("playwright_route_mock_har", "network_http_error", "likely_causes", "route/HAR miss can leak to live network and produce HTTP errors", 0.88)
    if {"network_http_error", "selector_drift"} <= categories:
        add_edge("network_http_error", "selector_drift", "blocks", "transport failure prevents reliable DOM/selector diagnosis", 0.86)
    if {"playwright_shadow_dom_locator", "selector_drift"} <= categories:
        add_edge("playwright_shadow_dom_locator", "selector_drift", "likely_causes", "shadow DOM boundary explains ordinary locator failure", 0.84)
    if {"website_change", "playwright_shadow_dom_locator"} <= categories:
        add_edge("website_change", "playwright_shadow_dom_locator", "likely_causes", "site DOM change can introduce a shadow/custom-element boundary", 0.82)
    if {"website_change", "selector_drift"} <= categories:
        add_edge("website_change", "selector_drift", "likely_causes", "site DOM change can make previous selectors stale", 0.82)
    if {"website_change", "response_shape_change"} <= categories:
        add_edge("website_change", "response_shape_change", "likely_causes", "site/API change explains downstream parser/schema symptoms", 0.86)
    if {"playwright_execution_context_destroyed", "selector_drift"} <= categories:
        add_edge("playwright_execution_context_destroyed", "selector_drift", "blocks", "runtime context loss can invalidate downstream locators", 0.82)

    if len(categories) > 1 and not edges:
        first = nodes[0]["id"] if nodes else "E1"
        for node in nodes[1:3]:
            edges.append(
                {
                    "from": first,
                    "to": node["id"],
                    "relation": "competes_with",
                    "confidence": 0.55,
                    "reason": "multiple weak signals lack a confident causal relationship",
                }
            )

    return {"schema_version": "evidence_graph/v1", "nodes": graph_nodes, "edges": edges}
