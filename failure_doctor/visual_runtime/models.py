from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


VISUAL_SCHEMA_VERSION = "visual_run/v1"


@dataclass
class VisualRun:
    root: Path
    manifest: dict[str, Any]
    screenshots_manifest: dict[str, Any]
    observations: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    clicks: list[dict[str, Any]] = field(default_factory=list)
    viewports: list[dict[str, Any]] = field(default_factory=list)
    dpr: list[dict[str, Any]] = field(default_factory=list)
    ocr: list[dict[str, Any]] = field(default_factory=list)
    vlm_responses: list[dict[str, Any]] = field(default_factory=list)
    dom_snapshots: list[Path] = field(default_factory=list)


SAFE_FAILURE_TYPES = {
    "visual_runtime_observation_lag",
    "stale_screenshot_action",
    "image_token_budget_exceeded",
    "screenshot_transport_overhead",
    "overcompressed_screenshot_loss",
    "underloaded_screenshot",
    "vlm_action_grounding_failure",
    "visual_element_misidentification",
    "coordinate_click_drift",
    "viewport_scroll_state_mismatch",
    "dpr_scaling_mismatch",
    "ocr_semantic_mismatch",
    "transient_ui_missed_between_frames",
    "visual_context_rot",
    "visual_dom_conflict",
    "pure_visual_insufficient_evidence",
    "visual_runtime_safety_blocked",
}
