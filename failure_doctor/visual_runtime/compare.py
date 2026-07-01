from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .loader import load_visual_run
from .profiler import profile_visual_run


def compare_visual_runs(baseline: Path, candidate: Path, out_dir: Path) -> dict[str, Any]:
    base_profile = profile_visual_run(load_visual_run(baseline, dom_optional=True))
    cand_profile = profile_visual_run(load_visual_run(candidate, dom_optional=True))
    report = {
        "schema_version": "visual_runtime_comparison/v1",
        "baseline_run_id": base_profile.get("run_id"),
        "candidate_run_id": cand_profile.get("run_id"),
        "baseline": base_profile,
        "candidate": cand_profile,
        "recommendation": _recommend(base_profile, cand_profile),
        "external_vlm_call_count": 0,
        "screenshot_upload_count": 0,
        "forbidden_output_count": 0,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "visual_runtime_comparison.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "visual_runtime_comparison.md").write_text(_render_compare_md(report), encoding="utf-8")
    _write_csv(out_dir / "latency_comparison.csv", ["run", "max_observation_latency_ms"], [
        ["baseline", base_profile["latency"]["max_observation_latency_ms"]],
        ["candidate", cand_profile["latency"]["max_observation_latency_ms"]],
    ])
    _write_csv(out_dir / "screenshot_cost_comparison.csv", ["run", "total_bytes", "tokens"], [
        ["baseline", base_profile["screenshot_cost"]["total_bytes"], base_profile["screenshot_cost"]["total_estimated_image_tokens"]],
        ["candidate", cand_profile["screenshot_cost"]["total_bytes"], cand_profile["screenshot_cost"]["total_estimated_image_tokens"]],
    ])
    _write_csv(out_dir / "action_grounding_comparison.csv", ["run", "max_click_point_error_px"], [
        ["baseline", base_profile["grounding"]["max_click_point_error_px"]],
        ["candidate", cand_profile["grounding"]["max_click_point_error_px"]],
    ])
    (out_dir / "recommendation.md").write_text("# Recommendation\n\n" + report["recommendation"] + "\n", encoding="utf-8")
    return report


def _recommend(base: dict[str, Any], cand: dict[str, Any]) -> str:
    base_error = base["grounding"]["max_click_point_error_px"]
    cand_error = cand["grounding"]["max_click_point_error_px"]
    if cand_error < base_error:
        return "Candidate has lower coordinate drift; prefer it after local verification."
    if cand_error > base_error:
        return "Baseline has lower coordinate drift; investigate candidate viewport or DPR metadata."
    return "Both runs have similar coordinate drift; compare stale-observation and screenshot-cost reports."


def _render_compare_md(report: dict[str, Any]) -> str:
    return f"""# Visual Runtime Comparison

- Baseline: `{report.get("baseline_run_id")}`
- Candidate: `{report.get("candidate_run_id")}`

{report.get("recommendation")}
"""


def _write_csv(path: Path, headers: list[str], rows: list[list[Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)
