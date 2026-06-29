"""Composite diagnosis engine with legacy diagnosis compatibility."""

from __future__ import annotations

from typing import Any, Mapping

from .candidates import collect_diagnosis_candidates
from .causal_policy import (
    build_repair_order,
    determine_blocking_failure,
    determine_primary_failure,
    determine_secondary_failures,
    identify_downstream_failures,
)
from .evidence_graph import build_evidence_graph
from .evidence_nodes import extract_evidence_nodes
from .classifier import classify_failure_artifact


def classify_composite_failure_artifact(artifact: Mapping[str, Any]) -> dict[str, Any]:
    nodes = extract_evidence_nodes(artifact)
    candidates = collect_diagnosis_candidates(artifact)
    graph = build_evidence_graph(nodes, candidates)
    causal_edges = [edge for edge in graph.get("edges", []) if edge.get("relation") in {"blocks", "likely_causes"} and float(edge.get("confidence", 0)) >= 0.6]
    if causal_edges:
        primary = determine_primary_failure(candidates, graph)
    else:
        legacy = classify_failure_artifact(artifact)
        primary = _candidate_for_legacy(candidates, legacy) or determine_primary_failure(candidates, graph)
    secondary = determine_secondary_failures(candidates, graph, primary)
    blocking = determine_blocking_failure(primary, secondary, graph)
    downstream = identify_downstream_failures(primary, secondary, graph)
    repair_order = build_repair_order(primary, secondary, graph)
    mode = "composite" if secondary and any(edge.get("relation") in {"blocks", "likely_causes"} for edge in graph.get("edges", [])) else "single"

    primary_failure = _public_failure(primary)
    secondary_failures = [_public_secondary(item) for item in secondary]
    result = {
        "schema_version": "composite_diagnosis/v2",
        "diagnosis_mode": mode,
        "primary_failure": primary_failure,
        "secondary_failures": secondary_failures,
        "blocking_failure": blocking,
        "downstream_failures": downstream,
        "competing_hypotheses": [_competing(item) for item in secondary if item.get("relationship_to_primary") == "competing"],
        "evidence_graph": graph,
        "repair_order": repair_order,
        "why_this_order": _why_this_order(primary_failure, repair_order),
        "confidence_reason": _confidence_reason(primary, graph),
        "score_breakdown": _score_breakdown(primary, graph),
        "why_not_other_categories": _why_not_other_categories(primary, secondary),
        "safe_next_action": True,
        # Legacy fields expected by existing CLI/tests.
        "failure_type": primary_failure["technical_category"],
        "technical_category": primary_failure["technical_category"],
        "subtype": primary_failure.get("subtype"),
        "confidence": primary_failure["confidence"],
        "evidence": list(primary.get("positive_evidence", [])) or [node["label"] for node in nodes[:3]],
        "suggested_fix": _suggestions(primary_failure["technical_category"], repair_order),
        "can_auto_fix": False,
        "synthetic_only": True,
    }
    if secondary_failures:
        result["alternative_diagnoses"] = [
            {"failure_type": item["technical_category"], "confidence": item["confidence"]} for item in secondary_failures
        ]
    return result


def _candidate_for_legacy(candidates: list[Mapping[str, Any]], legacy: Mapping[str, Any]) -> dict[str, Any] | None:
    legacy_type = legacy.get("failure_type") or legacy.get("technical_category")
    for candidate in candidates:
        if candidate.get("technical_category") == legacy_type:
            merged = dict(candidate)
            merged["confidence"] = float(legacy.get("confidence") or merged.get("confidence") or 0)
            merged["subtype"] = legacy.get("subtype") or merged.get("subtype")
            if isinstance(legacy.get("evidence"), list):
                merged["positive_evidence"] = list(legacy.get("evidence", []))
            return merged
    return None


def _public_failure(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "failure_layer": str(candidate.get("failure_layer") or "automation_engineering"),
        "technical_category": str(candidate.get("technical_category") or "insufficient_evidence"),
        "subtype": candidate.get("subtype"),
        "confidence": round(float(candidate.get("confidence") or 0), 2),
        "evidence_ids": list(candidate.get("evidence_ids", [])),
    }


def _public_secondary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    data = _public_failure(candidate)
    data["relationship_to_primary"] = str(candidate.get("relationship_to_primary") or "unresolved")
    if candidate.get("suppressed_by_primary"):
        data["suppressed_by_primary"] = True
        data["suppression_reason"] = str(candidate.get("suppression_reason") or "")
    return data


def _competing(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "technical_category": candidate.get("technical_category"),
        "subtype": candidate.get("subtype"),
        "confidence": round(float(candidate.get("confidence") or 0), 2),
        "why_not_primary": "causal relation confidence is too low, so this remains a competing hypothesis",
    }


def _why_this_order(primary: Mapping[str, Any], repair_order: list[str]) -> str:
    category = primary.get("technical_category")
    return f"Repair starts with {category} because blocking/root-cause evidence should be resolved before downstream symptoms."


def _confidence_reason(primary: Mapping[str, Any], graph: Mapping[str, Any]) -> str:
    edge_count = len(graph.get("edges", []))
    return (
        f"Primary={primary.get('technical_category')} confidence={primary.get('confidence')} "
        f"with {len(primary.get('evidence_ids', []))} evidence ids and {edge_count} graph edges."
    )


def _score_breakdown(primary: Mapping[str, Any], graph: Mapping[str, Any]) -> dict[str, float]:
    edge_bonus = min(len(graph.get("edges", [])) * 2, 8)
    structured = len(primary.get("evidence_ids", [])) * 5
    total = structured + edge_bonus + float(primary.get("confidence") or 0) * 10
    return {
        "structured_evidence_score": round(structured, 2),
        "timing_relation_score": round(edge_bonus, 2),
        "independent_source_score": 0,
        "negative_evidence_score": 0,
        "total_score": round(total, 2),
    }


def _why_not_other_categories(primary: Mapping[str, Any], secondary: list[Mapping[str, Any]]) -> list[str]:
    primary_type = primary.get("technical_category")
    if not secondary:
        return ["No stronger competing category had structured evidence."]
    return [
        f"{item.get('technical_category')} was kept as {item.get('relationship_to_primary', 'secondary')} because {primary_type} has higher blocking priority."
        for item in secondary[:5]
    ]


def _suggestions(category: str, repair_order: list[str]) -> list[str]:
    if category == "anti_bot_risk":
        return [
            "treat this as an access-control or anti-abuse boundary, not a selector bug",
            "use official API, authorized export, manual review, or stop automation if authorization is unclear",
        ]
    return repair_order or ["collect more structured evidence before changing code"]
