from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .diagnosis import diagnose_visual_run
from .image_metrics import screenshot_cost_report
from .loader import load_visual_run, validate_visual_run
from .profiler import profile_visual_run


def write_visual_runtime_report(
    input_dir: Path,
    out_dir: Path,
    *,
    no_dom: bool = False,
    dom_optional: bool = False,
    safety_evaluate: bool = False,
) -> dict[str, Any]:
    run = load_visual_run(input_dir, no_dom=no_dom, dom_optional=dom_optional)
    profile = profile_visual_run(run)
    diagnosis = diagnose_visual_run(run, no_dom=no_dom, safety_evaluate=safety_evaluate)
    cost = screenshot_cost_report(run)
    validation = validate_visual_run(input_dir, no_dom=no_dom, dom_optional=dom_optional)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "visual_runtime_profile.json": profile,
        "screenshot_cost_report.json": cost,
        "visual_runtime_diagnosis.json": diagnosis,
        "action_grounding_report.json": _action_grounding_report(run),
        "coordinate_drift_report.json": _coordinate_drift_report(run),
        "stale_observation_report.json": _stale_observation_report(run),
        "visual_context_loss_report.json": _context_loss_report(run),
        "visual_runtime_validation.json": validation,
    }
    for name, payload in outputs.items():
        (out_dir / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "diagnosis.md").write_text(_render_diagnosis_md(diagnosis), encoding="utf-8")
    (out_dir / "visual_runtime_profile.md").write_text(_render_profile_md(profile), encoding="utf-8")
    (out_dir / "screenshot_cost_report.md").write_text(_render_cost_md(cost), encoding="utf-8")
    (out_dir / "visual_timeline.md").write_text(_render_timeline_md(run), encoding="utf-8")
    (out_dir / "safe_next_actions.md").write_text(_render_next_actions(diagnosis), encoding="utf-8")
    (out_dir / "open_this_first_visual.md").write_text(_render_open_this_first(diagnosis), encoding="utf-8")
    return {"profile": profile, "diagnosis": diagnosis, "validation": validation, "out_dir": str(out_dir)}


def _action_grounding_report(run: Any) -> dict[str, Any]:
    outside = [item for item in run.clicks if item.get("inside_bbox") is False]
    return {"schema_version": "action_grounding_report/v1", "clicks": run.clicks, "outside_bbox_count": len(outside)}


def _coordinate_drift_report(run: Any) -> dict[str, Any]:
    return {"schema_version": "coordinate_drift_report/v1", "clicks": run.clicks, "dpr": run.dpr, "viewport": run.viewports}


def _stale_observation_report(run: Any) -> dict[str, Any]:
    stale = [item for item in run.observations if item.get("stale") is True]
    return {"schema_version": "stale_observation_report/v1", "stale_count": len(stale), "observations": run.observations}


def _context_loss_report(run: Any) -> dict[str, Any]:
    conflicts = [item for item in run.vlm_responses if item.get("context_conflict") is True]
    return {"schema_version": "visual_context_loss_report/v1", "context_conflict_count": len(conflicts), "vlm_responses": run.vlm_responses}


def _render_diagnosis_md(diagnosis: dict[str, Any]) -> str:
    evidence = "\n".join(f"- {item}" for item in diagnosis.get("evidence", []))
    plan = "\n".join(f"- {item}" for item in diagnosis.get("suggested_fix_plan", []))
    return f"""# Visual Runtime Diagnosis

Conclusion: `{diagnosis.get("subtype")}` at confidence `{diagnosis.get("confidence")}`.

## Evidence

{evidence}

## Safe Next Action

{diagnosis.get("safe_next_action")}

## Suggested Fix Plan

{plan}

## Verification

{diagnosis.get("verification_strategy")}
"""


def _render_profile_md(profile: dict[str, Any]) -> str:
    counts = profile.get("counts", {})
    return f"""# Visual Runtime Profile

- Run: `{profile.get("run_id")}`
- Source: `{profile.get("source")}`
- Mode: `{profile.get("mode")}`
- Frames: `{counts.get("frames")}`
- Actions: `{counts.get("actions")}`
- Clicks: `{counts.get("clicks")}`
"""


def _render_cost_md(cost: dict[str, Any]) -> str:
    return f"""# Screenshot Cost Report

- Frames: `{cost.get("frame_count")}`
- Total bytes: `{cost.get("total_bytes")}`
- Estimated image tokens: `{cost.get("total_estimated_image_tokens")}`
- Image token budget exceeded: `{cost.get("image_token_budget_exceeded")}`
"""


def _render_timeline_md(run: Any) -> str:
    lines = ["# Visual Timeline", ""]
    for item in run.observations:
        lines.append(f"- Observation `{item.get('step_id')}`: {item.get('summary', '')}")
    for item in run.actions:
        lines.append(f"- Action `{item.get('step_id')}`: {item.get('action', '')}")
    return "\n".join(lines) + "\n"


def _render_next_actions(diagnosis: dict[str, Any]) -> str:
    return f"""# Safe Next Actions

{diagnosis.get("safe_next_action")}

- Keep analysis local and offline.
- Do not upload screenshots unless the user explicitly authorizes a configured provider.
- If authorization or evidence is unclear, stop and ask for manual review.
"""


def _render_open_this_first(diagnosis: dict[str, Any]) -> str:
    return f"""# Open This First

Primary visual runtime subtype: `{diagnosis.get("subtype")}`.

Read `diagnosis.md`, then `visual_timeline.md`, then the JSON reports for profile,
screenshot cost, grounding, coordinate drift, stale observations, and context loss.
"""
