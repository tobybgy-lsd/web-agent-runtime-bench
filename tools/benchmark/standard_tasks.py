"""Public-safe standard task registry for WebAgentRuntimeBench."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    title: str
    description: str
    command: str
    expected_artifacts: tuple[str, ...]
    scoring_dimensions: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    baseline_family: str
    user_scenario: str
    synthetic_only: bool = True
    external_network_allowed: bool = False


STANDARD_TASKS: tuple[BenchmarkTask, ...] = (
    BenchmarkTask(
        task_id="static_extraction",
        title="Static Product List Extraction",
        description="Read a local HTML snapshot and compare extracted product fields against a fixed schema.",
        command="python -m json.tool examples\\static_product_list\\expected_output.json",
        expected_artifacts=("examples/static_product_list/expected_output.json",),
        scoring_dimensions=("task_success", "reproducibility", "safety_guard"),
        required_capabilities=("html_parsing", "schema_mapping"),
        baseline_family="naive_static_parser",
        user_scenario="Product detail or listing pages where fields are visible in HTML.",
    ),
    BenchmarkTask(
        task_id="dynamic_runtime_missing",
        title="Dynamic Runtime Missing Diagnosis",
        description="Classify why a synthetic JS bundle fails outside a browser runtime.",
        command=(
            "python demo\\phase5_2_runtime\\run_synthetic_runtime_demo.py "
            "--out-dir sample_run\\a0 --node node"
        ),
        expected_artifacts=("run_summary.json", "trace.jsonl", "failure_replay.md"),
        scoring_dimensions=("task_success", "diagnosis_accuracy", "repair_success", "reproducibility", "safety_guard"),
        required_capabilities=("runtime_diagnosis", "browser_shim"),
        baseline_family="no_shim_vs_full_shim",
        user_scenario="Debugging Agent failures on JavaScript-rendered pages.",
    ),
    BenchmarkTask(
        task_id="bundle_shim_repair",
        title="Bundle Shim Repair Variants",
        description="Run five synthetic bundles with missing runtime objects and verify full-shim recovery.",
        command=(
            "python demo\\phase5_2_runtime\\run_bundle_variant_cases.py "
            "--out-dir sample_run\\a2 --node node"
        ),
        expected_artifacts=("run_summary.json", "bundle_variant_results.json", "capability_dashboard.md"),
        scoring_dimensions=("task_success", "diagnosis_accuracy", "repair_success", "reproducibility", "safety_guard"),
        required_capabilities=("runtime_diagnosis", "shim_repair", "mock_api_verification"),
        baseline_family="partial_runtime_vs_full_runtime",
        user_scenario="Choosing which browser APIs a headless Agent runtime must provide.",
    ),
    BenchmarkTask(
        task_id="signed_mock_api",
        title="Signed Mock API Verification",
        description="Execute six local synthetic signed-API cases and reject tampered negative cases.",
        command=(
            "python demo\\phase5_2_runtime\\run_signed_api_benchmark.py "
            "--out-dir sample_run\\a3 --node node"
        ),
        expected_artifacts=("run_summary.json", "signed_api_results.json", "signed_api_trace.jsonl"),
        scoring_dimensions=("task_success", "diagnosis_accuracy", "negative_rejection", "reproducibility", "safety_guard"),
        required_capabilities=("signed", "signed_api", "dependency_tracing", "negative_verification"),
        baseline_family="positive_only_vs_negative_guarded",
        user_scenario="Understanding local API dependency tracing for request verification without real signatures.",
    ),
    BenchmarkTask(
        task_id="failure_diagnosis",
        title="Failure Diagnosis CLI",
        description="Classify known synthetic failure traces and generate repair prompts.",
        command=(
            "python tools\\diagnostics\\diagnose_failure.py "
            "--run-summary examples\\failure_diagnosis\\signed_api_failure_run_summary.json "
            "--trace examples\\failure_diagnosis\\signed_api_failure_trace.jsonl "
            "--out-dir sample_run\\diagnosis"
        ),
        expected_artifacts=("diagnosis.json", "diagnosis.md", "codex_repair_prompt.md"),
        scoring_dimensions=("task_success", "diagnosis_accuracy", "reproducibility", "safety_guard"),
        required_capabilities=("failure_replay", "rule_based_diagnosis"),
        baseline_family="manual_trace_inspection",
        user_scenario="Turning Agent failure traces into actionable repair instructions.",
    ),
    BenchmarkTask(
        task_id="safety_guard",
        title="Synthetic Safety Guard",
        description="Verify benchmark assets remain local-only and contain no real-platform credential logic.",
        command="powershell -ExecutionPolicy Bypass -File scripts\\local_safety_scan.ps1",
        expected_artifacts=("console_output",),
        scoring_dimensions=("task_success", "safety_guard", "reproducibility"),
        required_capabilities=("safety_scan", "release_gate"),
        baseline_family="no_safety_gate_vs_local_safety_gate",
        user_scenario="Public benchmark release review and artifact hygiene.",
    ),
)


def get_task(task_id: str) -> BenchmarkTask:
    for task in STANDARD_TASKS:
        if task.task_id == task_id:
            return task
    known = ", ".join(task.task_id for task in STANDARD_TASKS)
    raise KeyError(f"unknown benchmark task '{task_id}'. Known tasks: {known}")


def iter_task_ids(tasks: Iterable[BenchmarkTask] = STANDARD_TASKS) -> tuple[str, ...]:
    return tuple(task.task_id for task in tasks)
