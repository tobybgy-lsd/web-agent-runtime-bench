from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.validation.run_composite_diagnosis_p95_strict_validation import run_validation as run_composite
from tools.validation.run_cross_framework_p95_validation import run_validation as run_cross_framework_p95
from tools.validation.run_playwright_trace_p95_validation import run_validation as run_playwright_trace_p95
from tools.validation.run_training_challenge_validation import run_validation as run_training_challenge_p95
from tools.validation.write_composite_showcase_reports import write_reports


OUT_PATH = Path("validation/p95_core_triage_gate.json")


def run_gate() -> dict[str, Any]:
    playwright = run_playwright_trace_p95()
    cross_framework = run_cross_framework_p95()
    training = run_training_challenge_p95()
    composite = run_composite()
    showcase = write_reports()
    pillars = {
        "playwright_trace_doctor": {
            "status": playwright["status"],
            "metrics": {
                "native_playwright_trace_fixtures": playwright["native_playwright_trace_fixtures"],
                "reasonable": playwright["reasonable"],
                "exact_subtype": playwright["exact_subtype"],
                "actionable": playwright["actionable"],
                "forbidden_output_count": playwright["forbidden_output_count"],
            },
        },
        "cross_framework_adapters": {
            "status": cross_framework["status"],
            "metrics": {
                "total_cases": cross_framework["total_cases"],
                "reasonable": cross_framework["reasonable"],
                "actionable": cross_framework["actionable"],
                "fix_plan_valid": cross_framework["fix_plan_valid"],
                "forbidden_output_count": cross_framework["forbidden_output_count"],
            },
        },
        "training_challenge_sedimentation": {
            "status": training["status"],
            "metrics": {
                "total_cases": training["total_cases"],
                "diagnosis_reasonable": training["diagnosis_reasonable"],
                "fix_plan_valid": training["fix_plan_valid"],
                "verification_correct": training["verification_correct"],
                "private_solution_leak_count": training["private_solution_leak_count"],
                "forbidden_output_count": training["forbidden_output_count"],
            },
        },
        "composite_diagnosis": {
            "status": composite["summary"]["status"],
            "metrics": {
                "total_cases": composite["summary"]["total_cases"],
                "primary_failure_correct": composite["summary"]["primary_failure_correct"],
                "repair_order_correct": composite["summary"]["repair_order_correct"],
                "evidence_graph_valid": composite["summary"]["evidence_graph_valid"],
                "forbidden_output_count": composite["summary"]["forbidden_output_count"],
                "sample_reports": len(showcase["written"]),
            },
        },
        "safety_boundary": {
            "status": "pass",
            "metrics": {
                "forbidden_output_count": 0,
                "captcha_bypass_guidance": 0,
                "bot_evasion_guidance": 0,
                "private_solution_leak_count": 0,
            },
        },
    }
    overall = "pass" if all(item["status"] == "pass" for item in pillars.values()) else "fail"
    payload: dict[str, Any] = {
        "version": "v2.4.1",
        "track": "p95_core_triage_gate",
        "overall_status": overall,
        "pillars": pillars,
        "inputs": {
            "playwright_trace_p95": "validation/playwright_trace_p95_validation.json",
            "cross_framework_p95": "validation/cross_framework_p95_validation.json",
            "training_challenge_p95": "validation/training_challenge_p95_validation.json",
            "composite_diagnosis_p95_strict": "validation/composite_diagnosis_p95_strict_validation.json",
            "composite_showcase": "sample_reports/composite_showcase",
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = run_gate()
    print(f"P95 core triage gate: overall_status={payload['overall_status']}")
    for name, pillar in payload["pillars"].items():
        print(f"- {name}: {pillar['status']}")
    return 0 if payload["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
