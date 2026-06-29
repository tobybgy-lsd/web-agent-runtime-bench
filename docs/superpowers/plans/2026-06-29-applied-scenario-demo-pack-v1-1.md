# Applied Scenario Demo Pack v1.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local-only Applied Scenario Demo Pack that demonstrates diagnose, plan, verify, and regression-case workflows across six realistic business automation failure scenarios.

**Architecture:** Keep Agent Failure Doctor as the core product and add scenario fixtures under `examples/applied_scenarios/`. A validation runner executes existing `failure-doctor diagnose`, `plan`, and `verify` commands against each case, compares outputs with expected JSON files, and writes a release metric ledger. Tests enforce local-only safety boundaries and prevent claims that these demos are production business systems.

**Tech Stack:** Python standard library, existing `failure_doctor` CLI, unittest, JSON fixture files, Markdown docs.

---

### Task 1: Red Tests

**Files:**
- Create: `tests/test_applied_scenario_validation.py`
- Create: `tests/test_applied_scenario_safety.py`

- [ ] Write tests that fail until `examples/applied_scenarios/` exists, contains six scenario folders, and exposes at least eighteen runnable cases.
- [ ] Write tests that fail until `tools.validation.run_applied_scenario_validation` produces `validation/applied_scenario_validation.json`.
- [ ] Write tests that fail if applied scenario docs or generated outputs include forbidden bypass guidance, real platform credentials, authorization headers, phone numbers, or production platform domains.
- [ ] Run: `python -m unittest tests.test_applied_scenario_validation tests.test_applied_scenario_safety`
- [ ] Expected: FAIL because the v1.1 fixtures and runner do not exist yet.

### Task 2: Scenario Fixtures

**Files:**
- Create: `examples/applied_scenarios/README.md`
- Create directories:
  - `examples/applied_scenarios/01_hot_product_collector/`
  - `examples/applied_scenarios/02_live_commerce_monitor/`
  - `examples/applied_scenarios/03_ecommerce_listing_automation/`
  - `examples/applied_scenarios/04_content_publishing_workflow/`
  - `examples/applied_scenarios/05_gui_data_bridge/`
  - `examples/applied_scenarios/06_erp_ecommerce_sync/`

- [ ] Add three local-only cases per scenario.
- [ ] Each case includes `failed_run/`, `rerun_after_fix/`, `expected_diagnosis.json`, `expected_fix_plan.json`, `expected_verification.json`, and `regression_case.json`.
- [ ] Each scenario root includes top-level `failed_run/`, `rerun_after_fix/`, and expected JSON files copied from its primary case for quick manual demos.
- [ ] Ensure all sample logs and mock files use mock domains such as `local.mock` or relative files only.

### Task 3: Validation Runner

**Files:**
- Create: `tools/validation/run_applied_scenario_validation.py`

- [ ] Traverse `examples/applied_scenarios/*/cases/*`.
- [ ] For each case, run:
  - `failure_doctor diagnose <failed_run> --out <tmp_report>`
  - `failure_doctor plan <tmp_report> --out <tmp_plan>`
  - `failure_doctor verify --before <failed_run> --after <rerun_after_fix> --out <tmp_verify> --create-regression`
- [ ] Compare actual outputs to expected JSON.
- [ ] Write `validation/applied_scenario_validation.json`.
- [ ] Exit non-zero if fewer than 18 cases, diagnosis reasonable below 16, fix plans below 18, verification below 16, or forbidden output above 0.

### Task 4: Docs and Version

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `CHANGELOG.md`
- Modify: `validation/dashboard.md`
- Modify: `docs/VALIDATION_REPORT.md`
- Create: `docs/APPLIED_SCENARIO_DEMOS.md`
- Create: `docs/RESUME_AND_INTERVIEW_NOTES.md`
- Create: `docs/internal/CODEX_EXECUTION_REPORT_v1_1_APPLIED_SCENARIO_DEMO_PACK.md`

- [ ] Set package version to `1.1.0`.
- [ ] Keep README first screen short and add a small Applied Scenario Demos section.
- [ ] Add v1.1 changelog and dashboard rows.
- [ ] Document safety boundary: local-only mocks, no real platform scraping/posting, no anti-bot bypass.

### Task 5: Verification and Release Hygiene

**Commands:**
- `python -m pip install -e .`
- `python -m unittest discover -s tests -p "test_*.py"`
- `python -m tools.validation.run_real_trace_validation`
- `python -m tools.validation.run_external_public_reference_validation`
- `python -m tools.validation.run_resolution_validation`
- `python -m tools.validation.run_applied_scenario_validation`
- `failure-doctor diagnose examples/applied_scenarios/03_ecommerce_listing_automation/failed_run --out tmp_listing_report`
- `failure-doctor plan tmp_listing_report --out tmp_listing_plan`
- `failure-doctor verify --before examples/applied_scenarios/03_ecommerce_listing_automation/failed_run --after examples/applied_scenarios/03_ecommerce_listing_automation/rerun_after_fix --out tmp_listing_verify`
- `scripts\smoke_test.ps1`
- `scripts\local_safety_scan.ps1`

- [ ] Remove temporary reports after verification.
- [ ] Commit with `feat: add applied scenario demo pack`.
- [ ] Push and watch GitHub Actions to green.
