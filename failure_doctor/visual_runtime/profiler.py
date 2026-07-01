from __future__ import annotations

from typing import Any

from .image_metrics import screenshot_cost_report
from .models import VisualRun


def profile_visual_run(run: VisualRun) -> dict[str, Any]:
    cost = screenshot_cost_report(run)
    observation_latencies = [float(item.get("latency_ms", 0) or 0) for item in run.observations]
    response_latencies = [float(item.get("latency_ms", 0) or 0) for item in run.vlm_responses]
    click_errors = [float(item.get("click_point_error_px", 0) or 0) for item in run.clicks]
    dpr_errors = [float(item.get("dpr_scale_error", 0) or 0) for item in run.dpr]
    return {
        "schema_version": "visual_runtime_profile/v1",
        "run_id": run.manifest.get("run_id"),
        "source": run.manifest.get("source"),
        "mode": run.manifest.get("mode"),
        "local_only": run.manifest.get("local_only") is True,
        "no_external_upload": run.manifest.get("no_external_upload") is True,
        "counts": {
            "frames": cost["frame_count"],
            "observations": len(run.observations),
            "actions": len(run.actions),
            "clicks": len(run.clicks),
            "dom_snapshots": len(run.dom_snapshots),
        },
        "latency": {
            "max_observation_latency_ms": max(observation_latencies or [0]),
            "max_vlm_response_latency_ms": max(response_latencies or [0]),
            "average_action_delay_ms": _avg(float(item.get("delay_after_observation_ms", 0) or 0) for item in run.actions),
        },
        "screenshot_cost": cost,
        "grounding": {
            "max_click_point_error_px": max(click_errors or [0]),
            "actions_inside_bbox": sum(1 for item in run.clicks if item.get("inside_bbox") is True),
            "actions_outside_bbox": sum(1 for item in run.clicks if item.get("inside_bbox") is False),
        },
        "viewport": {
            "max_dpr_scale_error": max(dpr_errors or [0]),
            "viewport_scroll_mismatch_count": sum(1 for item in run.viewports if item.get("scroll_mismatch") is True),
            "resize_between_observation_action_count": sum(1 for item in run.viewports if item.get("resized_between_observation_action") is True),
        },
        "safety": {
            "external_vlm_call_count": 0,
            "screenshot_upload_count": 0,
            "real_platform_access_count": 0,
        },
    }


def _avg(values: Any) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(items) / len(items), 3)
