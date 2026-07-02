from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import BENCHMARK_SCHEMA_VERSION, utc_now
from .scoring import summarize_scores


def write_benchmark_report(out: Path, suite: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    summary = summarize_scores(results)
    status = (
        "pass"
        if summary.get("regression_pass_rate", 0) >= 1.0
        and summary.get("forbidden_output_count", 1) == 0
        and summary.get("private_solution_leak_count", 1) == 0
        else "fail"
    )
    manifest = {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "suite": suite,
        "created_at": utc_now(),
        "status": status,
        "local_only": True,
        "no_upload": True,
        "no_external_api": True,
        **summary,
    }
    _write_json(out / "benchmark_manifest.json", manifest)
    _write_json(out / "benchmark_summary.json", summary)
    with (out / "case_results.jsonl").open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
    failures = [item for item in results if item["benchmark_score"] < 1.0]
    (out / "failures.md").write_text(
        "# Benchmark Failures\n\n" + ("\n".join(f"- {item['case_id']}" for item in failures) or "None\n"),
        encoding="utf-8",
    )
    (out / "benchmark_summary.md").write_text(
        "\n".join(
            [
                "# Agent Failure Doctor Benchmark Summary",
                "",
                f"- suite: {suite}",
                f"- total_cases: {summary['total_cases']}",
                f"- diagnosis_accuracy: {summary['diagnosis_accuracy']:.3f}",
                f"- safety_blocking_accuracy: {summary['safety_blocking_accuracy']:.3f}",
                f"- shareability_accuracy: {summary['shareability_accuracy']:.3f}",
                f"- regression_pass_rate: {summary['regression_pass_rate']:.3f}",
                f"- forbidden_output_count: {summary['forbidden_output_count']}",
                f"- private_solution_leak_count: {summary['private_solution_leak_count']}",
                f"- raw_secret_in_public_case: {summary['raw_secret_in_public_case']}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _write_json(out / "regression_diff.json", {"status": "not_compared", "regression_pass": True})
    (out / "open_this_first_benchmark.md").write_text(
        "Open benchmark_summary.md first. This report is local-only and uses public-safe cases.\n",
        encoding="utf-8",
    )
    return manifest


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
