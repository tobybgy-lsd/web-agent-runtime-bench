# Android Mobile Stable v5.4-v6.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Android authoring, pilot, deep diagnostics, playbook, real-pilot, lab, and mobile-stability releases from v5.4.0 through v6.0.0 with public-safe validation and release artifacts.

**Architecture:** Follow the existing package pattern used by `failure_doctor/android_ops`: each release gets a focused package, CLI adapter, validation runner, docs, schemas, examples/templates, and P98 pillar integration. Keep every new Android surface local-only, dry-run by default, sanitized-by-default, and blocked for final submit or business mutation unless explicit review metadata exists.

**Tech Stack:** Python standard library, argparse CLI integration, JSON/YAML-like text outputs, existing validation scripts, PowerShell local safety scan, GitHub CLI release workflow, PyPI trusted publishing workflow.

---

### Task 1: Preserve Workspace Boundaries

**Files:**
- Read: `D:/WebAgentRuntimeBench-GitHub/git status`
- Do not modify: `validation/ocr_document_evidence_case_reports/**`, `.agents/**`, `validation/_android_synthetic/**`

- [ ] **Step 1: Confirm current branch and dirty files**

Run: `git status --short --untracked-files=normal`
Expected: Existing OCR report changes and untracked local folders may remain. They must not be staged.

- [ ] **Step 2: Confirm current stable base**

Run: `python -m failure_doctor --help`
Expected: CLI works before new modules are added.

### Task 2: Implement v5.4 Android Authoring

**Files:**
- Create: `failure_doctor/android_authoring/*.py`
- Create: `tools/validation/run_android_authoring_validation.py`
- Create: `validation/android_authoring_validation.json`
- Create: `docs/RELEASE_NOTES_v5.4.0.md`
- Modify: `failure_doctor/cli.py`
- Modify: `tools/validation/run_p98_master_gate.py`
- Test: `tests/test_android_authoring_v54.py`

- [ ] **Step 1: Add `android-author` CLI**

Implement commands for record, flow draft/edit/validate, assertion run, golden capture/diff, business preview, mutation diff, review queue, robustness, visual QA, and acceptance scaffold/run.

- [ ] **Step 2: Add public-safe core behavior**

Implement redacted recording, dry-run flow drafts, local/mock visual assertions, sanitized golden diffs, safe review queue, safe draft mode, robustness advice, and acceptance packs.

- [ ] **Step 3: Add validation and P98 pillars**

Add `android_flow_authoring`, `android_visual_assertions`, and `android_human_review_queue` with at least 300 declared cases and zero unsafe counters.

- [ ] **Step 4: Run v5.4 tests**

Run: `python -m unittest tests.test_android_authoring_v54`
Expected: PASS.

### Task 3: Implement v5.5 Android Pilot

**Files:**
- Create: `failure_doctor/android_pilot/*.py`
- Create: `tools/validation/run_android_pilot_validation.py`
- Create: `validation/android_pilot_validation.json`
- Create: `docs/RELEASE_NOTES_v5.5.0.md`
- Modify: `failure_doctor/cli.py`
- Modify: `tools/validation/run_p98_master_gate.py`
- Test: `tests/test_android_pilot_v55.py`

- [ ] **Step 1: Add `android-pilot` CLI**

Implement project init, onboarding from dump, app discovery, pack list/scaffold, data map/validate, draft run, review, acceptance, app-version-check, outcome, handoff-pack, and runbook generation.

- [ ] **Step 2: Add pilot safety defaults**

Ensure all pilot projects are local-only, no-upload, dry-run by default, final submit blocked by default, business mutation blocked by default, and sanitized handoff only.

- [ ] **Step 3: Add validation and P98 pillars**

Add `android_app_specific_pilot`, `android_business_workflow_pack`, and `android_pilot_acceptance_gate` with at least 340 declared cases and zero unsafe counters.

### Task 4: Implement v5.6 Android Deep Diagnostics

**Files:**
- Create: `failure_doctor/android_dx/*.py`
- Create: `tools/validation/run_android_deep_diagnostics_validation.py`
- Create: `validation/android_deep_diagnostics_validation.json`
- Create: `docs/RELEASE_NOTES_v5.6.0.md`
- Modify: `failure_doctor/cli.py`
- Modify: `tools/validation/run_p98_master_gate.py`
- Test: `tests/test_android_dx_v56.py`

- [ ] **Step 1: Add `android-dx` CLI**

Implement bundle create/validate, timeline, device, appium, ui-tree, locator, permission, webview, input, media, performance, business-state, root-cause, retryability, diagnose, report, and explain.

- [ ] **Step 2: Add evidence-bound diagnostics**

Generate diagnostic bundles, evidence index, timeline reports, layer diagnostics, root-cause graph, retryability decisions, and sanitized deep diagnosis report.

- [ ] **Step 3: Add validation and P98 pillars**

Add `android_deep_diagnostics`, `android_root_cause_forensics`, and `android_retryability_classifier` with at least 360 declared cases and zero unsafe counters.

### Task 5: Implement v5.7-v6.0 Stabilization Releases

**Files:**
- Create: `failure_doctor/android_playbooks/*.py`
- Create: `failure_doctor/android_real_pilot/*.py`
- Create: `failure_doctor/android_lab/*.py`
- Create: `failure_doctor/mobile_stability/*.py`
- Create: validation runners for playbooks, real pilot, lab, and mobile stability.
- Modify: `failure_doctor/cli.py`
- Modify: `tools/validation/run_p98_master_gate.py`
- Test: `tests/test_android_road_to_mobile_stable_v57_v60.py`

- [ ] **Step 1: Add `android-playbook`**

Map Android DX findings to safe remediation playbooks, role-specific views, verification checklist, and manual review checklist.

- [ ] **Step 2: Add `android-real-pilot`**

Create private pilot workspace helpers, intake, exclusion, sanitized import, dry-run checklist, sanitizer, acceptance, and public summary. Public examples must remain mock/synthetic.

- [ ] **Step 3: Add `android-lab`**

Create mock device lab workspace, daily health, long-run mock report, recovery metrics, trend, utilization, flaky report, and maintenance runbook.

- [ ] **Step 4: Add `mobile-stability`**

Add stable Android CLI/schema/plugin ABI registry checks, compatibility report, migration guide, and deprecation report.

### Task 6: Version, Docs, Validation, Build, Publish

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `CHANGELOG.md`
- Modify: `validation/dashboard.md`
- Modify: `docs/P98_CONTROLLED_MATURITY_RESULTS.md`
- Create: release notes and execution reports for each release.

- [ ] **Step 1: Run full validation**

Run:
`python -m unittest discover -s tests -p "test_*.py"`
`python -m tools.validation.run_p98_master_gate`
`python -m tools.validation.run_package_private_content_scan`
`powershell -ExecutionPolicy Bypass -File scripts/local_safety_scan.ps1`

- [ ] **Step 2: Build and check package**

Run:
`python -m build`
`python -m twine check dist/*`

- [ ] **Step 3: Clean venv install**

Install the built wheel and verify `failure-doctor --help` plus all new command groups.

- [ ] **Step 4: Publish sequential releases**

Only after all gates pass, push commits and publish versions in order: v5.4.0, v5.5.0, v5.6.0, v5.7.0, v5.8.0, v5.9.0, v6.0.0.

