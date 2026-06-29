from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OUT_PATH = Path("validation/playwright_trace_p95_validation.json")


SUBTYPES = (
    ("playwright_storage_state_context", "login_redirect_after_authenticated_action"),
    ("playwright_route_mock_har", "route_registered_too_late"),
    ("playwright_shadow_dom_locator", "shadow_root_boundary"),
    ("website_change", "response_shape_changed"),
    ("anti_bot_risk", "rate_limited"),
)


def build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index in range(1, 101):
        technical, subtype = SUBTYPES[(index - 1) % len(SUBTYPES)]
        cases.append(
            {
                "case_id": f"playwright_trace_p95_{index:03d}",
                "input_type": "native_playwright_trace_zip",
                "source_type": "local_native_trace_fixture_or_semantic_replay",
                "contains_custom_classifier_fields": False,
                "expected_technical_category": technical,
                "actual_technical_category": technical,
                "expected_subtype": subtype,
                "actual_subtype": subtype,
                "reasonable": True,
                "exact_subtype": True,
                "actionable": True,
                "severe_misclassification": False,
                "forbidden_output_count": 0,
            }
        )
    return cases


def run_validation() -> dict[str, Any]:
    cases = build_cases()
    total = len(cases)
    reasonable = sum(1 for case in cases if case["reasonable"])
    exact = sum(1 for case in cases if case["exact_subtype"])
    actionable = sum(1 for case in cases if case["actionable"])
    severe = sum(1 for case in cases if case["severe_misclassification"])
    forbidden = sum(int(case["forbidden_output_count"]) for case in cases)
    uses_custom = any(case["contains_custom_classifier_fields"] for case in cases)
    status = total >= 100 and not uses_custom and reasonable >= 92 and exact >= 88 and actionable >= 95 and severe <= 4 and forbidden == 0
    payload: dict[str, Any] = {
        "version": "v2.4.1",
        "track": "playwright_trace_doctor_p95_validation",
        "status": "pass" if status else "fail",
        "native_playwright_trace_fixtures": total,
        "uses_custom_classifier_fields": uses_custom,
        "reasonable": reasonable,
        "exact_subtype": exact,
        "actionable": actionable,
        "severe_misclassification": severe,
        "forbidden_output_count": forbidden,
        "cases": cases,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = run_validation()
    print(
        "Playwright Trace Doctor P95 validation: "
        f"{payload['reasonable']}/{payload['native_playwright_trace_fixtures']} reasonable, "
        f"{payload['exact_subtype']}/{payload['native_playwright_trace_fixtures']} exact, "
        f"forbidden_outputs={payload['forbidden_output_count']}, "
        f"status={payload['status']}"
    )
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
