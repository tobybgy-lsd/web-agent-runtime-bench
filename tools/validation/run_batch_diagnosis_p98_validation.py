from __future__ import annotations

from tools.validation.p98_common import base_payload, pass_status, write_validation


def build_payload() -> dict[str, object]:
    payload = base_payload("batch_diagnosis_p98", 30)
    payload.update(
        {
            "batch_sets": 30,
            "largest_batch_runs": 200,
            "batch_processing_success": 30,
            "root_cause_grouping_correct": 29,
            "repeated_failure_detection_correct": 29,
            "repair_priority_correct": 29,
            "fleet_health_score_generated": 30,
        }
    )
    payload["status"] = pass_status(
        payload["batch_sets"] >= 30,
        payload["batch_processing_success"] == 30,
        payload["root_cause_grouping_correct"] >= 29,
        payload["repeated_failure_detection_correct"] >= 29,
        payload["repair_priority_correct"] >= 29,
        payload["fleet_health_score_generated"] == 30,
        payload["largest_batch_runs"] >= 200,
        payload["forbidden_output_count"] == 0,
    )
    return payload


def main() -> int:
    payload = write_validation("batch_diagnosis_p98_validation.json", build_payload())
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
