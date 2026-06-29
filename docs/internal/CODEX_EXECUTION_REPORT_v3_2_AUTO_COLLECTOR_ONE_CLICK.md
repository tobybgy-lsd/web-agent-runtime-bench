# Codex Execution Report: v3.2 Auto Collector & One-Click Diagnosis

## Goal

Upgrade Agent Failure Doctor from the v3.1.0 P98 diagnostic core to v3.2.0 with authorized local collection, one-click Windows diagnosis, watch mode, and an auto collector P98 pillar.

## New CLI Commands

- `failure-doctor collect --project <dir> --preset auto --out <report> --auto-diagnose --auto-handoff --auto-sanitize`
- `failure-doctor watch --project <dir> --out <reports> --once --auto-diagnose`
- `failure-doctor run --capture -- <command>`

## Collector Behavior

- Writes `collection_manifest.json`, `collection_summary.md`, `open_this_first.md`, `raw_local_only_do_not_share/`, `sanitized_failure_pack/`, optional `report/`, `fix_plan/`, and `ai_handoff/`.
- Supports presets for Playwright, Selenium, Scrapy, requests/httpx, Node browser automation, generic RPA, and auto detection.
- Allows output directories inside the selected project while taking a pre-collection source snapshot and skipping the output directory to prevent self-collection.

## Safety Boundary

- Local-only and no upload.
- Project-scoped, not whole-computer scanning.
- Skips `.git`, `node_modules`, virtualenvs, cache folders, browser profiles, credential stores, cookie stores, and SSH key material.
- Shareable output remains `sanitized_failure_pack/` and still requires human review.
- Anti-bot/access-control output remains detection and safe routing only.

## Validation Metrics

- Unit tests: `341/341` pass.
- Auto collector validation: `95` cases, `95/95` collection success, `95/95` preset detection, `95/95` manifest schema valid.
- Auto collector safety metrics: out-of-scope files collected `0`, browser profile files collected `0`, raw secrets in sanitized output `0`, forbidden outputs `0`.
- P98 master gate: `overall_status=pass`, `controlled_maturity_score=98`, current stable line `v3.2.0`.
- P95 core triage gate: `overall_status=pass`.
- Smoke test: PASS.
- Local safety scan: PASS.
- Manual smoke: collect/watch passed; `run --capture` generated diagnosis and fix plan while returning the wrapped command's expected exit code `1`.

## Version Decision

`pyproject.toml`, README, CHANGELOG, validation dashboard, release notes, and P98 gate now align on v3.2.0.

## Known Limits

- Screenshot input is metadata-first; no image understanding was added.
- Watch mode is polling-based and conservative.
- The collector prepares diagnosis, fix plans, and AI handoff packs; it does not automatically patch source code.
- Ecosystem maturity remains excluded from the controlled maturity score.

## Next Steps

- Publish the v3.2.0 release manually after GitHub Actions is green.
- Consider optional local HTML report viewer later, after collecting external feedback on the one-click collector flow.
