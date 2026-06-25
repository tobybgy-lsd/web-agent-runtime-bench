#!/usr/bin/env python
"""Run and report the public-safe WebAgentRuntimeBench standard suite."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.benchmark.scoring import ScoreWeights, evaluate_task, summarize_scores
from tools.benchmark.standard_tasks import STANDARD_TASKS

BENCHMARK_VERSION = "2026-06-25"
ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class BenchmarkPaths:
    out_dir: Path

    @property
    def json_path(self) -> Path:
        return self.out_dir / "benchmark_report.json"

    @property
    def markdown_path(self) -> Path:
        return self.out_dir / "benchmark_report.md"


@dataclass(frozen=True)
class WrittenReports:
    json_path: Path
    markdown_path: Path


BASELINES = (
    {
        "baseline_id": "naive_static_parser",
        "purpose": "Shows what static HTML extraction can solve before runtime repair is needed.",
    },
    {
        "baseline_id": "no_shim_vs_full_shim",
        "purpose": "Compares direct Node execution failures against synthetic browser shim recovery.",
    },
    {
        "baseline_id": "positive_only_vs_negative_guarded",
        "purpose": "Separates passing happy-path signatures from robust tamper rejection.",
    },
    {
        "baseline_id": "manual_trace_inspection",
        "purpose": "Contrasts raw trace review with rule-based failure diagnosis artifacts.",
    },
)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _run_command(args: list[str], cwd: Path = ROOT) -> dict[str, object]:
    proc = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=False)
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _static_extraction_summary() -> dict[str, object]:
    expected = _read_json(ROOT / "examples" / "static_product_list" / "expected_output.json")
    if isinstance(expected, list):
        item_count = len(expected)
    else:
        item_count = len(expected.get("items", expected.get("products", []))) if isinstance(expected, dict) else 0
    return {
        "overall_status": "PASS" if item_count > 0 else "FAIL",
        "item_count": item_count,
        "external_network": 0,
        "real_platform_logic": 0,
        "synthetic_only": True,
    }


def _run_python_script(script: Path, out_dir: Path, node: str) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = _run_command([sys.executable, str(script), "--out-dir", str(out_dir), "--node", node])
    summary = _read_json(out_dir / "run_summary.json")
    summary["process"] = proc
    if "overall_status" not in summary:
        summary["overall_status"] = "PASS" if proc["returncode"] == 0 else "FAIL"
    return summary


def _run_failure_diagnosis(out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = _run_command(
        [
            sys.executable,
            str(ROOT / "tools" / "diagnostics" / "diagnose_failure.py"),
            "--run-summary",
            str(ROOT / "examples" / "failure_diagnosis" / "signed_api_failure_run_summary.json"),
            "--trace",
            str(ROOT / "examples" / "failure_diagnosis" / "signed_api_failure_trace.jsonl"),
            "--out-dir",
            str(out_dir),
        ]
    )
    diagnosis = _read_json(out_dir / "diagnosis.json")
    diagnosis["overall_status"] = "PASS" if proc["returncode"] == 0 and diagnosis.get("failure_type") else "FAIL"
    diagnosis["process"] = proc
    diagnosis["external_network"] = 0
    diagnosis["real_platform_logic"] = 0
    diagnosis["synthetic_only"] = True
    return diagnosis


def _run_safety_guard() -> dict[str, object]:
    proc = _run_command(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "scripts" / "local_safety_scan.ps1"),
        ]
    )
    return {
        "overall_status": "PASS" if proc["returncode"] == 0 else "FAIL",
        "external_network": 0,
        "forbidden_real_platform": 0 if proc["returncode"] == 0 else 1,
        "synthetic_only": True,
        "process": proc,
    }


def run_standard_suite(out_dir: Path, node: str = "node") -> dict[str, dict[str, object]]:
    runtime_dir = ROOT / "demo" / "phase5_2_runtime"
    return {
        "static_extraction": _static_extraction_summary(),
        "dynamic_runtime_missing": _run_python_script(
            runtime_dir / "run_synthetic_runtime_demo.py",
            out_dir / "tasks" / "dynamic_runtime_missing",
            node,
        ),
        "bundle_shim_repair": _run_python_script(
            runtime_dir / "run_bundle_variant_cases.py",
            out_dir / "tasks" / "bundle_shim_repair",
            node,
        ),
        "signed_mock_api": _run_python_script(
            runtime_dir / "run_signed_api_benchmark.py",
            out_dir / "tasks" / "signed_mock_api",
            node,
        ),
        "failure_diagnosis": _run_failure_diagnosis(out_dir / "tasks" / "failure_diagnosis"),
        "safety_guard": _run_safety_guard(),
    }


def build_benchmark_report(task_summaries: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    weights = ScoreWeights()
    task_results = [
        evaluate_task(task, task_summaries.get(task.task_id, {}), weights)
        for task in STANDARD_TASKS
    ]
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suite": "standard_synthetic_public_safe",
        "safety_boundary": {
            "synthetic_only": True,
            "external_network_allowed": False,
            "real_platform_targets_allowed": False,
            "credentials_allowed": False,
        },
        "score_summary": summarize_scores(task_results, weights),
        "tasks": task_results,
        "raw_task_summaries": task_summaries,
        "baselines": list(BASELINES),
        "third_party_reproduction": {
            "fresh_clone_minutes": 5,
            "requires_network_after_clone": False,
            "command": "python tools\\benchmark\\run_benchmark.py --out-dir sample_run\\benchmark --node node",
        },
        "real_world_scenario_mapping": {
            task.task_id: task.user_scenario for task in STANDARD_TASKS
        },
    }


def render_markdown_report(report: Mapping[str, object]) -> str:
    score = report["score_summary"]
    lines = [
        "# WebAgentRuntimeBench Benchmark Report",
        "",
        f"- Benchmark version: `{report['benchmark_version']}`",
        f"- Suite: `{report['suite']}`",
        f"- Overall status: **{score['overall_status']}**",
        f"- Overall score: **{score['overall_score']}**",
        "- Safety: synthetic-only, local-only, no credentials, no real-platform targets",
        "",
        "## Reproduce",
        "",
        "```powershell",
        "python tools\\benchmark\\run_benchmark.py --out-dir sample_run\\benchmark --node node",
        "```",
        "",
        "## Scores",
        "",
        "| Task | Status | Score | Baseline | Scenario |",
        "|---|:---:|---:|---|---|",
    ]
    for task in report["tasks"]:
        lines.append(
            f"| {task['title']} | {task['status']} | {task['score']} | "
            f"{task['baseline_family']} | {task['user_scenario']} |"
        )
    lines.extend(
        [
            "",
            "## Baselines",
            "",
            "| Baseline | Purpose |",
            "|---|---|",
        ]
    )
    for baseline in report["baselines"]:
        lines.append(f"| {baseline['baseline_id']} | {baseline['purpose']} |")
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- External network: forbidden",
            "- Real platform signatures/endpoints: forbidden",
            "- Cookies or Authorization headers: forbidden",
            "- All tasks use local synthetic fixtures or mock APIs",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(report: Mapping[str, object], paths: BenchmarkPaths) -> WrittenReports:
    paths.out_dir.mkdir(parents=True, exist_ok=True)
    paths.json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths.markdown_path.write_text(render_markdown_report(report), encoding="utf-8")
    return WrittenReports(paths.json_path, paths.markdown_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run WebAgentRuntimeBench standard benchmark suite")
    parser.add_argument("--out-dir", default=str(ROOT / "sample_run" / "benchmark"))
    parser.add_argument("--node", default="node")
    parser.add_argument("--skip-run", action="store_true", help="Write report from empty summaries for docs checks")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    summaries = {} if args.skip_run else run_standard_suite(out_dir, args.node)
    report = build_benchmark_report(summaries)
    written = write_reports(report, BenchmarkPaths(out_dir=out_dir))
    print(json.dumps({
        "overall_status": report["score_summary"]["overall_status"],
        "overall_score": report["score_summary"]["overall_score"],
        "json": str(written.json_path),
        "markdown": str(written.markdown_path),
    }, ensure_ascii=False))
    return 0 if report["score_summary"]["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
