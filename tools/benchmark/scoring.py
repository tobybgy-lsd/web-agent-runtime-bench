"""Scoring protocol for standard WebAgentRuntimeBench tasks."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Mapping

from .standard_tasks import BenchmarkTask


@dataclass(frozen=True)
class ScoreWeights:
    task_success: float = 0.35
    diagnosis_accuracy: float = 0.20
    repair_success: float = 0.15
    negative_rejection: float = 0.15
    safety_guard: float = 0.10
    reproducibility: float = 0.05

    def for_dimensions(self, dimensions: tuple[str, ...]) -> dict[str, float]:
        raw = {name: getattr(self, name) for name in dimensions}
        total = sum(raw.values())
        if total <= 0:
            return {name: 0.0 for name in dimensions}
        return {name: value / total for name, value in raw.items()}


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 1.0 if numerator > 0 else 0.0
    return max(0.0, min(1.0, numerator / denominator))


def _task_success(summary: Mapping[str, object]) -> float:
    if summary.get("overall_status") == "PASS":
        return 1.0
    if summary.get("status") == "pass":
        return 1.0
    return 0.0


def _diagnosis_accuracy(task: BenchmarkTask, summary: Mapping[str, object]) -> float:
    if task.task_id == "bundle_shim_repair":
        return _ratio(float(summary.get("classified_failures", 0)), float(summary.get("failure_cases", 5)))
    if task.task_id == "dynamic_runtime_missing":
        return 1.0 if summary.get("classifier", {}).get("error_type") not in (None, "unknown_runtime_error") else 0.0
    if task.task_id == "signed_mock_api":
        return _ratio(float(summary.get("verified_cases", 0)), float(summary.get("total_cases", 6)))
    if task.task_id == "failure_diagnosis":
        return 1.0 if summary.get("failure_type") not in (None, "unknown") else 0.0
    return _task_success(summary)


def _repair_success(task: BenchmarkTask, summary: Mapping[str, object]) -> float:
    if task.task_id == "dynamic_runtime_missing":
        return 1.0 if summary.get("with_shim_run", {}).get("success") is True else 0.0
    if task.task_id == "bundle_shim_repair":
        return _ratio(float(summary.get("full_shim_success_count", 0)), 5.0)
    return _task_success(summary)


def _negative_rejection(summary: Mapping[str, object]) -> float:
    return _ratio(float(summary.get("negative_rejected", 0)), float(summary.get("negative_cases", 0)))


def _safety_guard(summary: Mapping[str, object]) -> float:
    safe = (
        summary.get("external_network", 0) == 0
        and summary.get("real_platform_logic", summary.get("forbidden_real_platform", 0)) == 0
        and summary.get("synthetic_only", True) is True
    )
    return 1.0 if safe else 0.0


def _reproducibility(summary: Mapping[str, object]) -> float:
    return 1.0 if summary else 0.0


def evaluate_task(
    task: BenchmarkTask,
    summary: Mapping[str, object] | None,
    weights: ScoreWeights | None = None,
) -> dict[str, object]:
    weights = weights or ScoreWeights()
    summary = summary or {}
    dimension_values: dict[str, float] = {}
    for dimension in task.scoring_dimensions:
        if dimension == "task_success":
            dimension_values[dimension] = _task_success(summary)
        elif dimension == "diagnosis_accuracy":
            dimension_values[dimension] = _diagnosis_accuracy(task, summary)
        elif dimension == "repair_success":
            dimension_values[dimension] = _repair_success(task, summary)
        elif dimension == "negative_rejection":
            dimension_values[dimension] = _negative_rejection(summary)
        elif dimension == "safety_guard":
            dimension_values[dimension] = _safety_guard(summary)
        elif dimension == "reproducibility":
            dimension_values[dimension] = _reproducibility(summary)
        else:
            raise ValueError(f"unknown scoring dimension: {dimension}")

    normalized_weights = weights.for_dimensions(task.scoring_dimensions)
    score = sum(dimension_values[name] * normalized_weights[name] for name in task.scoring_dimensions) * 100
    status = "PASS" if score == 100.0 else "FAIL"
    return {
        "task_id": task.task_id,
        "title": task.title,
        "status": status,
        "score": round(score, 2),
        "dimensions": dimension_values,
        "scoring_dimensions": task.scoring_dimensions,
        "baseline_family": task.baseline_family,
        "user_scenario": task.user_scenario,
        "command": task.command,
        "synthetic_only": task.synthetic_only,
        "external_network_allowed": task.external_network_allowed,
    }


def summarize_scores(results: list[Mapping[str, object]], weights: ScoreWeights | None = None) -> dict[str, object]:
    scores = [float(result.get("score", 0.0)) for result in results]
    passed = sum(1 for result in results if result.get("status") == "PASS")
    overall = round(mean(scores), 2) if scores else 0.0
    return {
        "task_count": len(results),
        "passed_tasks": passed,
        "failed_tasks": len(results) - passed,
        "overall_score": overall,
        "overall_status": "PASS" if results and passed == len(results) else "FAIL",
        "weights": (weights or ScoreWeights()).__dict__,
    }
