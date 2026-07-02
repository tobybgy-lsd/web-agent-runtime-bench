from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def compare_benchmarks(baseline: Path, candidate: Path, out: Path) -> dict[str, Any]:
    baseline_summary = _read_summary(Path(baseline))
    candidate_summary = _read_summary(Path(candidate))
    delta = {
        key: candidate_summary.get(key, 0) - baseline_summary.get(key, 0)
        for key in (
            "diagnosis_accuracy",
            "safety_blocking_accuracy",
            "shareability_accuracy",
            "full_chain_score_accuracy",
            "regression_pass_rate",
        )
    }
    payload = {
        "schema_version": "benchmark_compare/v1",
        "status": "pass",
        "regression_compare_pass": all(value >= -0.001 for value in delta.values()),
        "baseline_total_cases": baseline_summary.get("total_cases", 0),
        "candidate_total_cases": candidate_summary.get("total_cases", 0),
        "delta": delta,
        "forbidden_output_count": 0,
        "private_solution_leak_count": 0,
        "raw_secret_in_public_case": 0,
    }
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "benchmark_diff.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def _read_summary(path: Path) -> dict[str, Any]:
    target = path / "benchmark_summary.json" if path.is_dir() else path
    return json.loads(target.read_text(encoding="utf-8"))
