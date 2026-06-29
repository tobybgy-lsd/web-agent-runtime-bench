# Failure Resolution Loop v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a v1.0 loop that turns diagnosis reports into fix plans, verifies before/after reruns, and emits safe regression cases.

**Architecture:** Keep diagnosis unchanged and add a focused `tools.failure_artifacts.resolution` module for fix-plan generation, verification, markdown rendering, and regression case creation. Extend `failure_doctor.cli` with `plan` and `verify` subcommands. Add local-only before/after fixtures plus a runner that produces `validation/resolution_validation_12.json`.

**Tech Stack:** Python stdlib, existing `failure_doctor` CLI and `tools.failure_artifacts` modules, `unittest`, PowerShell smoke/safety scripts.

---

### Task 1: Schemas and Fix Plan Generation

**Files:**
- Create: `schemas/fix_plan.schema.json`
- Create: `schemas/verification_report.schema.json`
- Create: `tools/failure_artifacts/resolution.py`
- Test: `tests/test_resolution_schemas.py`
- Test: `tests/test_fix_plan_generation.py`

- [ ] Write failing tests for required schema fields and sample validation.
- [ ] Implement schema files.
- [ ] Implement `generate_fix_plan(diagnosis, evidence=None)` for core failure types.
- [ ] Verify anti-bot plans are safe and insufficient-evidence plans request artifacts.

### Task 2: Plan CLI

**Files:**
- Modify: `failure_doctor/cli.py`
- Test: `tests/test_failure_doctor_plan_cli.py`

- [ ] Add failing CLI tests for `failure-doctor plan <report> --out <dir>`.
- [ ] Add parser subcommand and implementation.
- [ ] Output `fix_plan.json`, `fix_plan.md`, and `codex_fix_prompt.md`.

### Task 3: Verification and Regression Case

**Files:**
- Create: `tools/failure_artifacts/regression_case.py`
- Modify: `tools/failure_artifacts/resolution.py`
- Modify: `failure_doctor/cli.py`
- Test: `tests/test_resolution_verifier.py`
- Test: `tests/test_failure_doctor_verify_cli.py`
- Test: `tests/test_regression_case_generation.py`
- Test: `tests/test_resolution_safety_boundary.py`

- [ ] Add failing tests for resolved, not_resolved, changed_failure, insufficient evidence, and anti-bot compliant handling.
- [ ] Implement `verify_resolution` and markdown rendering.
- [ ] Implement `failure-doctor verify --before ... --after ... --out ... [--create-regression]`.
- [ ] Generate `regression_case.json` with `safe_to_publish=false`.

### Task 4: Validation Fixtures and Runner

**Files:**
- Create: `examples/resolution_validation_cases/*`
- Create: `tools/validation/run_resolution_validation.py`
- Create: `validation/resolution_validation_12.json`
- Test: `tests/test_resolution_validation_runner.py`

- [ ] Add 12 local before/after cases.
- [ ] Add runner and result JSON.
- [ ] Verify at least 10/12 status matches and forbidden output is 0.

### Task 5: Docs, CI, Verification, Commit

**Files:**
- Modify: `.github/workflows/benchmark.yml`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `validation/dashboard.md`
- Modify: `docs/VALIDATION_REPORT.md`
- Create: `docs/internal/CODEX_EXECUTION_REPORT_v1_0_FAILURE_RESOLUTION_LOOP.md`

- [ ] Add docs for `diagnose -> plan -> verify`.
- [ ] Add runner to CI.
- [ ] Run unit tests, smoke, safety, and CI.
- [ ] Commit `feat: add failure resolution loop`.
