# Integration Pack v1.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add workflow integration adapters that turn Playwright test-results, browser-use/agent logs, and generic raw log folders into Agent Failure Doctor failure packs.

**Architecture:** Keep `failure-doctor diagnose` as the core diagnosis entrypoint. Add small local-only collectors under `integrations/` that copy or normalize existing artifacts into the same file layout already supported by Failure Doctor: `error.log`, `console.txt`, `network.json`, `user_description.txt`, screenshot metadata, and optional `trace.zip`. Extend the CLI with `collect-playwright` and `pack-logs` commands while exposing the browser-use adapter as an importable module.

**Tech Stack:** Python standard library, existing `failure_doctor` CLI, unittest, JSON/Markdown fixtures.

---

### Task 1: Red Tests

**Files:**
- Create: `tests/test_playwright_collector.py`
- Create: `tests/test_browser_use_adapter.py`
- Create: `tests/test_generic_log_pack_adapter.py`
- Create: `tests/test_github_action_docs.py`
- Create: `tests/test_integration_safety.py`

- [ ] Write tests for `failure-doctor collect-playwright <test-results> --out <failure_pack>`.
- [ ] Write tests for `failure-doctor pack-logs <raw_logs> --out <failure_pack>`.
- [ ] Write tests for `integrations.browser_use.adapter.convert_browser_use_run`.
- [ ] Write tests for GitHub Action usage documentation.
- [ ] Write tests that scan integration outputs/docs for forbidden bypass guidance and secret-like data.
- [ ] Run: `python -m unittest tests.test_playwright_collector tests.test_browser_use_adapter tests.test_generic_log_pack_adapter tests.test_github_action_docs tests.test_integration_safety`
- [ ] Expected: FAIL because integration modules and CLI commands do not exist yet.

### Task 2: Playwright Collector

**Files:**
- Create: `integrations/playwright/collector.py`
- Create: `integrations/playwright/README.md`
- Modify: `failure_doctor/cli.py`

- [ ] Implement `collect_playwright_artifacts(test_results, out_dir)`.
- [ ] Detect and copy `trace.zip`, `error.log`, `console.txt`, screenshot files, and useful JSON summaries.
- [ ] Normalize Playwright report files into `error.log`, `network.json`, `user_description.txt`, and `input_summary.json`.
- [ ] Add CLI command `failure-doctor collect-playwright`.

### Task 3: Generic Log Pack Adapter

**Files:**
- Create: `integrations/generic_log_pack/adapter.py`
- Create: `integrations/generic_log_pack/README.md`
- Modify: `failure_doctor/cli.py`

- [ ] Implement `pack_generic_logs(raw_logs, out_dir)`.
- [ ] Copy recognized `error.log`, `console.txt`, `network.json`, screenshots, and description/readme files.
- [ ] Write `input_summary.json` with observed evidence, missing evidence, and evidence priority.
- [ ] Add CLI command `failure-doctor pack-logs`.

### Task 4: Browser-use / Agent Adapter

**Files:**
- Create: `integrations/browser_use/adapter.py`
- Create: `integrations/browser_use/README.md`

- [ ] Implement `convert_browser_use_run(input_path, out_dir)`.
- [ ] Support `agent_history.json` and `.log` files.
- [ ] Emit `error.log`, `user_description.txt`, `agent_steps.json`, and `input_summary.json`.
- [ ] Ensure output can be diagnosed by `failure-doctor diagnose`.

### Task 5: GitHub Action Usage Docs

**Files:**
- Create: `.github/actions/failure-doctor-diagnose/action.yml`
- Create: `docs/GITHUB_ACTION_USAGE.md`
- Create: `docs/INTEGRATIONS.md`

- [ ] Add a composite action that installs the package, runs `failure-doctor diagnose`, and uploads report files when used by a workflow.
- [ ] Document local-first behavior and safe boundaries.

### Task 6: Verification

**Commands:**
- `python -m unittest discover -s tests -p "test_*.py"`
- `python -m tools.validation.run_applied_scenario_validation`
- `failure-doctor collect-playwright examples/mock_playwright_test_results --out tmp_failure_pack`
- `failure-doctor diagnose tmp_failure_pack --out tmp_collected_report`
- `failure-doctor pack-logs examples/mock_raw_logs --out tmp_log_pack`
- `failure-doctor diagnose tmp_log_pack --out tmp_log_report`
- `scripts\smoke_test.ps1`
- `scripts\local_safety_scan.ps1`

- [ ] Remove temporary report directories.
- [ ] Commit with `feat: add workflow integration adapters`.
- [ ] Push and watch GitHub Actions to green.
