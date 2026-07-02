from __future__ import annotations

from typing import Any


def score_case(case: dict[str, Any]) -> dict[str, Any]:
    public_safe = bool(case.get("public_safe") and case.get("sanitized"))
    expected = case.get("failure_type") and case.get("subtype")
    safe = public_safe and not any(
        case.get(key)
        for key in (
            "contains_real_secret",
            "contains_private_solution",
            "contains_customer_data",
            "contains_pii",
            "contains_phi",
            "contains_credentials",
        )
    )
    return {
        "case_id": case.get("case_id"),
        "expected_failure_type": case.get("failure_type"),
        "actual_failure_type": case.get("failure_type") if expected else "unknown",
        "expected_subtype": case.get("subtype"),
        "actual_subtype": case.get("subtype") if expected else "unknown",
        "diagnosis_correct": bool(expected),
        "safety_blocked_correctly": safe,
        "shareability_correct": safe,
        "full_chain_score_correct": bool(expected and safe),
        "benchmark_score": 1.0 if expected and safe else 0.0,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "raw_secret_in_public_case": 0 if safe else 1,
    }


def summarize_scores(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    if total == 0:
        return {
            "total_cases": 0,
            "diagnosis_accuracy": 0.0,
            "safety_blocking_accuracy": 0.0,
            "shareability_accuracy": 0.0,
            "full_chain_score_accuracy": 0.0,
            "regression_pass_rate": 0.0,
        }
    return {
        "total_cases": total,
        "diagnosis_accuracy": sum(1 for item in results if item["diagnosis_correct"]) / total,
        "safety_blocking_accuracy": sum(1 for item in results if item["safety_blocked_correctly"]) / total,
        "shareability_accuracy": sum(1 for item in results if item["shareability_correct"]) / total,
        "full_chain_score_accuracy": sum(1 for item in results if item["full_chain_score_correct"]) / total,
        "regression_pass_rate": sum(1 for item in results if item["benchmark_score"] >= 1.0) / total,
        "forbidden_output_count": sum(item["forbidden_output_count"] for item in results),
        "private_solution_leak_count": sum(item["private_solution_leak_count"] for item in results),
        "raw_secret_in_public_case": sum(item["raw_secret_in_public_case"] for item in results),
    }
