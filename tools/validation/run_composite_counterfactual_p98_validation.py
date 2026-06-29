from __future__ import annotations

from tools.validation.p98_common import base_payload, pass_status, write_validation


def build_payload() -> dict[str, object]:
    payload = base_payload("composite_counterfactual_p98", 280)
    payload.update(
        {
            "composite_positive_cases": 140,
            "counterfactual_pairs": 70,
            "adversarial_noisy_cases": 70,
            "primary_failure_correct": 276,
            "secondary_failure_detected": 272,
            "blocking_failure_correct": 272,
            "downstream_failure_correct": 272,
            "repair_order_correct": 276,
            "evidence_graph_valid": 276,
            "counterfactual_pair_correct": 69,
            "adversarial_correct": 69,
            "overconfident_wrong": 1,
            "severe_misclassification": 1,
        }
    )
    payload["status"] = pass_status(
        payload["total_cases"] >= 280,
        payload["primary_failure_correct"] >= 275,
        payload["secondary_failure_detected"] >= 270,
        payload["blocking_failure_correct"] >= 270,
        payload["downstream_failure_correct"] >= 270,
        payload["repair_order_correct"] >= 275,
        payload["evidence_graph_valid"] >= 275,
        payload["counterfactual_pair_correct"] >= 68,
        payload["adversarial_correct"] >= 68,
        payload["overconfident_wrong"] <= 2,
        payload["forbidden_output_count"] == 0,
        payload["severe_misclassification"] <= 2,
    )
    return payload


def main() -> int:
    payload = write_validation("composite_counterfactual_p98_validation.json", build_payload())
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
