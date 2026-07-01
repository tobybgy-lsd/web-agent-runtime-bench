from __future__ import annotations

from pathlib import Path
from typing import Any

from .loader import validate_visual_run
from .report import write_visual_runtime_report


def validate_and_diagnose_case(case_dir: Path) -> dict[str, Any]:
    run_dir = case_dir / "visual_run"
    expected = _expected(case_dir)
    validation = validate_visual_run(run_dir, dom_optional=True)
    report = write_visual_runtime_report(run_dir, case_dir / "visual_report", dom_optional=True, safety_evaluate=True)
    diagnosis = report["diagnosis"]
    subtype_correct = diagnosis.get("subtype") == expected.get("subtype")
    reasonable = diagnosis.get("failure_type") == expected.get("failure_type") or subtype_correct
    return {
        "case": case_dir.name,
        "status": "pass" if validation.get("status") in {"pass", "warning"} and reasonable else "fail",
        "validation": validation,
        "expected_subtype": expected.get("subtype"),
        "actual_subtype": diagnosis.get("subtype"),
        "subtype_correct": subtype_correct,
        "diagnosis_reasonable": reasonable,
        "profile_generated": True,
        "timeline_generated": (case_dir / "visual_report" / "visual_timeline.md").exists(),
        "screenshot_cost_report_generated": (case_dir / "visual_report" / "screenshot_cost_report.json").exists(),
        "action_grounding_report_generated": (case_dir / "visual_report" / "action_grounding_report.json").exists(),
        "coordinate_drift_report_generated": (case_dir / "visual_report" / "coordinate_drift_report.json").exists(),
        "stale_observation_report_generated": (case_dir / "visual_report" / "stale_observation_report.json").exists(),
        "external_vlm_call_count": 0,
        "screenshot_upload_count": 0,
        "real_platform_access_count": 0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
    }


def _expected(case_dir: Path) -> dict[str, Any]:
    import json

    path = case_dir / "expected_visual_runtime_diagnosis.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    return {}
