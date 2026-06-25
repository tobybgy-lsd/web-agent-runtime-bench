# Benchmark Credibility Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn WebAgentRuntimeBench from a public-safe showcase into a reproducible benchmark package with standard tasks, scoring, baselines, CI reporting, third-party reproduction docs, and real-world scenario mapping.

**Architecture:** Add a small Python benchmark runner under `tools/benchmark/` that executes the existing synthetic demos as named tasks, evaluates outputs with a transparent scoring protocol, and writes JSON/Markdown reports. Add docs and GitHub Actions around that runner without introducing real-platform targets or network dependencies.

**Tech Stack:** Python standard library, existing demo scripts, PowerShell smoke scripts, GitHub Actions.

---

### Task 1: Standard Task Registry and Scoring Model

**Files:**
- Create: `tools/benchmark/__init__.py`
- Create: `tools/benchmark/standard_tasks.py`
- Create: `tools/benchmark/scoring.py`
- Test: `tests/test_benchmark_scoring.py`

- [ ] **Step 1: Write failing tests**

Run: `python -m unittest tests.test_benchmark_scoring -v`
Expected: FAIL because `tools.benchmark` does not exist.

- [ ] **Step 2: Implement registry and scoring**

Define standard task metadata for static extraction, dynamic runtime missing, bundle variants, signed mock API, failure diagnosis, and safety guard. Implement deterministic weighted scoring with dimensions: task_success, diagnosis_accuracy, repair_success, negative_rejection, safety_guard, reproducibility.

- [ ] **Step 3: Run tests**

Run: `python -m unittest tests.test_benchmark_scoring -v`
Expected: PASS.

### Task 2: Benchmark Runner and Reports

**Files:**
- Create: `tools/benchmark/run_benchmark.py`
- Test: `tests/test_benchmark_runner.py`
- Create: `sample_reports/benchmark_ci_report_sample.md`

- [ ] **Step 1: Write failing runner tests**

Run: `python -m unittest tests.test_benchmark_runner -v`
Expected: FAIL because runner functions are missing.

- [ ] **Step 2: Implement runner**

Run existing local synthetic checks where practical and write `benchmark_report.json` and `benchmark_report.md` with task results, scoring summary, baselines, safety posture, and reproduction commands.

- [ ] **Step 3: Run runner tests**

Run: `python -m unittest tests.test_benchmark_runner -v`
Expected: PASS.

### Task 3: Baselines, Protocol, Reproduction, and Scenario Docs

**Files:**
- Create: `docs/benchmark_tasks.md`
- Create: `docs/scoring_protocol.md`
- Create: `docs/baselines.md`
- Create: `docs/reproducibility.md`
- Create: `docs/real_world_scenario_mapping.md`
- Modify: `README.md`
- Modify: `docs/roadmap.md`

- [ ] **Step 1: Document the six credibility layers**

Explain the standard task suite, scoring protocol, comparison baselines, reproduction workflow, CI report, and real-world mapping while preserving the synthetic-only safety boundary.

- [ ] **Step 2: Link docs from README**

Add a concise benchmark section and quick command.

### Task 4: CI Report

**Files:**
- Create: `.github/workflows/benchmark.yml`
- Modify: `.gitignore`

- [ ] **Step 1: Add CI workflow**

Run unit tests, smoke test, safety scan, and benchmark runner. Upload benchmark reports as artifacts.

- [ ] **Step 2: Ignore generated benchmark outputs**

Keep generated outputs out of commits while preserving sample reports.

### Task 5: Verification, Commit, Push

**Commands:**
- `python -m unittest discover -s tests -v`
- `python tools\benchmark\run_benchmark.py --out-dir sample_run\benchmark --node node`
- `.\scripts\smoke_test.ps1`
- `.\scripts\local_safety_scan.ps1`
- `git status --short`
- `git add ...`
- `git commit -m "feat: add benchmark credibility layer"`
- `git push origin main`

Expected: all checks pass, only intentional files staged, push succeeds.
