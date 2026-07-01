from __future__ import annotations

from typing import Any

from .models import VisualRun
from .profiler import profile_visual_run
from .safety import evaluate_visual_safety


def diagnose_visual_run(run: VisualRun, *, no_dom: bool = False, safety_evaluate: bool = False) -> dict[str, Any]:
    profile = profile_visual_run(run)
    safety = evaluate_visual_safety(run)
    if safety_evaluate and safety["shareability"] == "blocked":
        return _diagnosis(
            "visual_runtime_safety_blocked",
            "visual_runtime_safety_blocked",
            0.98,
            ["sensitive screenshot, OCR, or VLM-response evidence requires sanitization"],
            "Stop sharing this artifact until sensitive visual evidence is redacted or removed.",
            profile,
            safety,
            risk="high",
        )

    subtype, confidence, evidence = _select_subtype(run, profile, no_dom=no_dom)
    return _diagnosis(
        subtype,
        subtype,
        confidence,
        evidence,
        _safe_next_action(subtype),
        profile,
        safety,
        risk="medium" if subtype not in {"pure_visual_insufficient_evidence"} else "low",
    )


def _select_subtype(run: VisualRun, profile: dict[str, Any], *, no_dom: bool) -> tuple[str, float, list[str]]:
    text = _all_text(run)
    cost = profile["screenshot_cost"]
    if cost.get("image_token_budget_exceeded"):
        return "image_token_budget_exceeded", 0.89, ["estimated image-token budget exceeded"]
    if cost.get("transport_overhead_score", 0) >= 0.75 or "transport overhead" in text:
        return "screenshot_transport_overhead", 0.84, ["screenshot payload size or transfer cost is high"]
    for frame in cost.get("frames", []):
        if frame.get("overcompressed") or "overcompressed" in text:
            return "overcompressed_screenshot_loss", 0.87, ["screenshot quality score is low or compression artifacts were reported"]
        if frame.get("underloaded") or "underloaded" in text:
            return "underloaded_screenshot", 0.84, ["screenshot frame is empty or underloaded"]
    if any(item.get("stale") is True for item in run.observations) or "stale" in text:
        return "stale_screenshot_action", 0.91, ["action was generated from stale screenshot evidence"]
    if any(float(item.get("delay_after_observation_ms", 0) or 0) > 1500 for item in run.actions):
        return "visual_runtime_observation_lag", 0.86, ["action delay after observation exceeded threshold"]
    if any(float(item.get("dpr_scale_error", 0) or 0) > 0.1 for item in run.dpr) or "dpr" in text:
        return "dpr_scaling_mismatch", 0.92, ["device pixel ratio mapping drift was observed"]
    if any(item.get("scroll_mismatch") is True for item in run.viewports) or "scroll mismatch" in text:
        return "viewport_scroll_state_mismatch", 0.9, ["viewport scroll state changed between observation and action"]
    if any(item.get("inside_bbox") is False for item in run.clicks) or any(float(item.get("click_point_error_px", 0) or 0) > 12 for item in run.clicks):
        return "coordinate_click_drift", 0.92, ["click point landed outside target bbox or exceeded pixel drift threshold"]
    if "ocr mismatch" in text or "ocr_semantic_mismatch" in text:
        return "ocr_semantic_mismatch", 0.82, ["OCR excerpt conflicts with the intended action label"]
    if "misidentified" in text or "wrong element" in text:
        return "visual_element_misidentification", 0.85, ["visual observation selected the wrong visible element"]
    if "transient" in text or "missed between frames" in text:
        return "transient_ui_missed_between_frames", 0.81, ["UI state existed between captured frames"]
    if "context rot" in text or "memory conflict" in text:
        return "visual_context_rot", 0.83, ["visual context drift or memory conflict was reported"]
    if not no_dom and run.dom_snapshots and ("dom conflict" in text or "visual_dom_conflict" in text):
        return "visual_dom_conflict", 0.88, ["visual evidence conflicts with optional DOM snapshot"]
    if no_dom and not run.clicks and not run.vlm_responses:
        return "pure_visual_insufficient_evidence", 0.45, ["pure visual run lacks click, OCR, or VLM-response evidence"]
    return "vlm_action_grounding_failure", 0.78, ["visual action grounding evidence is inconclusive or low confidence"]


def _diagnosis(
    failure_type: str,
    subtype: str,
    confidence: float,
    evidence: list[str],
    next_action: str,
    profile: dict[str, Any],
    safety: dict[str, Any],
    *,
    risk: str,
) -> dict[str, Any]:
    return {
        "schema_version": "visual_runtime_diagnosis/v1",
        "failure_type": failure_type,
        "subtype": subtype,
        "evidence": evidence,
        "risk_level": risk,
        "confidence": confidence,
        "safe_next_action": next_action,
        "suggested_fix_plan": [
            "Re-run with the same offline artifact capture settings.",
            "Check screenshot freshness, viewport/DPR metadata, and action-coordinate mapping before changing app code.",
            "If evidence is insufficient, request a fuller local visual-run pack and manual review.",
        ],
        "verification_strategy": "Capture a new local visual-run artifact and compare profile, grounding, coordinate, and stale-observation reports.",
        "profile_summary": profile,
        "shareability": safety.get("shareability"),
        "external_vlm_call_count": 0,
        "screenshot_upload_count": 0,
        "real_platform_access_count": 0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
    }


def _safe_next_action(subtype: str) -> str:
    if subtype == "pure_visual_insufficient_evidence":
        return "Manual review required: add OCR, click metadata, viewport/DPR, or adjacent frames before classifying the run."
    if subtype == "visual_runtime_safety_blocked":
        return "Sanitize or remove sensitive visual evidence before sharing or handing the pack to another tool."
    return "Inspect the offline visual timeline and repair the capture/grounding/coordinate pipeline with local evidence only."


def _all_text(run: VisualRun) -> str:
    chunks: list[str] = []
    for collection in (run.observations, run.actions, run.clicks, run.viewports, run.dpr, run.ocr, run.vlm_responses):
        for item in collection:
            chunks.append(" ".join(str(value) for value in item.values()))
    return "\n".join(chunks).lower()
