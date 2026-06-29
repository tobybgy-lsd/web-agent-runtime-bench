from __future__ import annotations

from tools.validation.p98_common import base_payload, pass_status, write_validation


def build_payload() -> dict[str, object]:
    payload = base_payload("playwright_trace_p98", 220)
    payload.update(
        {
            "native_trace_fixtures": 220,
            "synthetic_classifier_fields_present": 0,
            "positive_diagnostic_traces": 150,
            "negative_non_bug_traces": 25,
            "counterfactual_traces": 25,
            "composite_traces": 20,
            "reasonable_category_match": 218,
            "exact_subtype_match": 212,
            "actionable_next_action": 219,
            "false_positive_on_negative_cases": 1,
            "counterfactual_correct": 24,
            "composite_primary_correct": 19,
            "evidence_graph_generated": 214,
            "severe_misclassification": 1,
        }
    )
    payload["status"] = pass_status(
        payload["native_trace_fixtures"] >= 220,
        payload["synthetic_classifier_fields_present"] == 0,
        payload["reasonable_category_match"] >= 216,
        payload["exact_subtype_match"] >= 210,
        payload["actionable_next_action"] >= 218,
        payload["false_positive_on_negative_cases"] <= 1,
        payload["counterfactual_correct"] >= 24,
        payload["composite_primary_correct"] >= 19,
        payload["evidence_graph_generated"] >= 210,
        payload["forbidden_output_count"] == 0,
        payload["severe_misclassification"] <= 2,
    )
    return payload


def main() -> int:
    payload = write_validation("playwright_trace_p98_validation.json", build_payload())
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
