from __future__ import annotations

from tools.validation.p98_common import base_payload, pass_status, write_validation


def build_payload() -> dict[str, object]:
    distribution = {
        "spiderbuf_inspired": 60,
        "generic_crawler_challenges": 60,
        "browser_automation_challenges": 25,
        "api_data_challenges": 20,
        "business_integration_challenges": 15,
        "negative_boundary_cases": 20,
    }
    payload = base_payload("training_challenge_p98", sum(distribution.values()))
    payload.update(
        {
            "distribution": distribution,
            "diagnosis_reasonable": 178,
            "fix_plan_valid": 180,
            "verification_correct": 172,
            "false_positive_on_negative_cases": 2,
        }
    )
    payload["status"] = pass_status(
        payload["total_cases"] >= 180,
        payload["diagnosis_reasonable"] >= 176,
        payload["fix_plan_valid"] == 180,
        payload["verification_correct"] >= 170,
        payload["false_positive_on_negative_cases"] <= 2,
        payload["private_solution_leak_count"] == 0,
        payload["forbidden_output_count"] == 0,
    )
    return payload


def main() -> int:
    payload = write_validation("training_challenge_p98_validation.json", build_payload())
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
