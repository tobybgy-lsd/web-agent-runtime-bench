# Agent Failure Doctor

[中文文档](README.zh-CN.md)

![CI](https://github.com/tobybgy-lsd/web-agent-runtime-bench/actions/workflows/benchmark.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Local-first failure diagnosis, repair planning, and fix verification for AI browser automation, Playwright, crawler, RPA, and business automation runs.

Current stable milestone: Agent Failure Doctor v2.5.0 AI Handoff & Patch Proposal Pack

Input:
trace.zip / error.log / console.txt / network.json / screenshot metadata / user_description.txt

Output:
diagnosis, evidence, next action, repair suggestions, GitHub issue draft, Codex fix prompt.
v2.5 also adds AI handoff task packs and dry-run patch proposals.

Core commands:
`failure-doctor diagnose` / `failure-doctor plan` / `failure-doctor handoff` / `failure-doctor propose-patch` / `failure-doctor verify` / `failure-doctor run` / `failure-doctor sanitize` / `failure-doctor adapt`

Lifecycle:
`capture/adapt -> diagnose -> plan -> AI handoff / patch proposal -> verify -> sanitize/share`

```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python -m pip install -e .
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

See [validation/dashboard.md](validation/dashboard.md) for release-level validation metrics and [validation/external_validation_dashboard.md](validation/external_validation_dashboard.md) for accepted external failure cases.

Composite diagnosis:
Agent Failure Doctor can report primary, secondary, blocking, and downstream failures for complex cases. It keeps legacy single-failure fields for compatibility, while exposing an evidence graph and repair order for advanced diagnosis.

Show the v2.1 lifecycle:

```powershell
failure-doctor diagnose .\examples\applied_scenarios\03_ecommerce_listing_automation\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor handoff .\report --target codex --out .\ai_handoff
failure-doctor propose-patch --repo . --report .\report --out .\patch_plan
failure-doctor verify --before .\examples\applied_scenarios\03_ecommerce_listing_automation\failed_run --after .\examples\applied_scenarios\03_ecommerce_listing_automation\rerun_after_fix --out .\verification
failure-doctor sanitize .\report --out .\shareable_pack
failure-doctor run -- python .\examples\mock_script_fails.py
```

Agent Failure Doctor uses a deterministic evidence-based diagnostic engine. It does not claim to solve arbitrary failures, but it provides explainable classification, evidence, fix plans, and before/after verification for known automation failure patterns.

Applied scenario demos are local-only mock workflows for commerce automation, live monitoring, content publishing, GUI data bridge, and ERP sync failure diagnosis.
Spiderbuf-inspired challenge demos are local-only mock failure packs inspired by public crawler-training challenge categories; they validate diagnosis and safe next actions without accessing spiderbuf.cn or publishing private solution logic.

Integration commands:
`failure-doctor collect-playwright` / `failure-doctor pack-logs` / `failure-doctor adapt`

## What You Get

```text
report/
|-- diagnosis.json
|-- diagnosis.md
|-- evidence.json
|-- input_summary.json
|-- issue_draft.md
|-- repair_suggestions.md
|-- codex_fix_prompt.md
`-- failure_doctor_report.zip
```

Agent Failure Doctor turns sanitized automation failure materials into a report that explains what likely failed, what evidence supports the diagnosis, what evidence is missing, and what to ask Codex or another coding assistant to change next.

## One-Minute Start

Auto Capture:

```powershell
failure-doctor run -- python crawler.py
failure-doctor run -- pytest tests/test_listing.py
failure-doctor run -- playwright test
```

This writes a local run folder under `.failure-doctor/runs/<run_id>/`:

```text
.failure-doctor/runs/<run_id>/
|-- command.txt
|-- exit_code.txt
|-- stdout.log
|-- stderr.log
|-- environment.json
|-- detected_artifacts.json
|-- input_summary.json
|-- diagnosis/
|-- fix_plan/
|-- verification_hint.md
`-- shareable_failure_pack.zip
```

The generated `safe_to_share.json` defaults to `safe_to_share=false`; review and sanitize before sending a pack to anyone else.

Sanitize & Share Pack:

Sanitize a failed run before sharing it:

```powershell
failure-doctor sanitize .\.failure-doctor\runs\<run_id> --out .\shareable_failure_pack
```

This writes redacted logs, redacted network summaries, trace metadata only, a redaction report, a review gate, and `shareable_failure_pack.zip`. Raw `trace.zip` archives are not copied into the sanitized pack.

Put a failed run in a folder:

```text
my_failed_run/
|-- error.log
|-- console.txt
|-- network.json
|-- README.txt
`-- screenshot.png
```

Then run:

```powershell
failure-doctor diagnose .\my_failed_run --out .\report
```

The tool inventories inputs and uses this evidence priority:

```text
trace.zip > log > network.json > user description > screenshot metadata
```

When evidence is too thin, it should downgrade to `insufficient_evidence` instead of guessing.

## Minimal Demos

Proxy/network failure:

```powershell
failure-doctor diagnose .\examples\failed_runs\proxy_failed --out .\report_proxy
```

Strict mode locator conflict:

```powershell
failure-doctor diagnose .\examples\failed_runs\strict_mode_locator --out .\report_locator
```

Low-evidence screenshot-only run:

```powershell
failure-doctor diagnose .\examples\failed_runs\low_evidence_screenshot_only --out .\report_low_evidence
```

Native Playwright trace fixture:

```powershell
trace-doctor diagnose .\examples\realistic_playwright_traces\02_login_redirect_302\trace.zip --out .\report_login_trace
```

## Before / After Report

Report structure: conclusion / evidence / why / next action / Codex fix prompt

Before:

```text
page.goto: net::ERR_PROXY_CONNECTION_FAILED while opening https://example.test
```

After:

```text
Conclusion: network/proxy setup failed before the page loaded.
Evidence: Playwright reported net::ERR_PROXY_CONNECTION_FAILED.
Next action: check proxy settings, DNS, VPN, and CI network configuration.
Codex fix prompt: add trace/log capture and make proxy configuration explicit.
```

## Verify a Fix

```powershell
failure-doctor diagnose .\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification_report
```

`verify` compares before/after evidence and reports whether the original failure is resolved, unchanged, changed into another failure, or insufficiently evidenced.

## AI Handoff & Patch Proposal

Turn a report into task packs that Codex, Claude Code, or Cursor can execute:

```powershell
failure-doctor handoff .\report --target codex --out .\ai_handoff
failure-doctor handoff .\report --target claude_code --out .\ai_handoff
failure-doctor handoff .\report --target cursor --out .\ai_handoff
```

This writes:

```text
ai_handoff/
|-- ai_handoff.json
|-- ai_handoff.md
|-- codex_task.md
|-- claude_code_task.md
|-- cursor_task.md
|-- affected_files.json
|-- validation_commands.md
|-- forbidden_actions.md
|-- token_budget_report.json
`-- ai_handoff_pack.zip
```

Generate a dry-run patch proposal without modifying source code:

```powershell
failure-doctor propose-patch --repo . --report .\report --out .\patch_plan
```

This writes:

```text
patch_plan/
|-- patch_proposal.md
|-- proposed_changes.json
|-- affected_files.json
|-- validation_commands.md
`-- patch_risk_assessment.json
```

`propose-patch` is intentionally proposal-only. It does not edit files, apply patches, run tests, or open pull requests.

v2.5 validation writes `validation/ai_handoff_validation.json`:

```text
20/20 Codex task files generated
20/20 Claude Code task files generated
20/20 Cursor task files generated
18/20 patch proposals generated
20/20 required sections present
20/20 concise token budget checks pass
0 forbidden outputs
```

## Applied Scenario Demos

Local-only mock demos show how Agent Failure Doctor can diagnose failures in:

- hot product collection
- live commerce monitoring
- ecommerce listing automation
- authorized content publishing workflow
- GUI / RPA data bridge
- ERP-to-ecommerce sync

Run:

```powershell
python -m tools.validation.run_applied_scenario_validation
```

## Spiderbuf-Inspired Challenge Demos

`examples/spiderbuf_inspired_challenges/` contains local-only mock failure packs inspired by public crawler-training challenge categories:

- cookie/session required
- iframe extraction
- Ajax dynamic loading
- random CSS selector drift
- infinite scroll missing items
- rate limit 429
- API signature required
- browser fingerprint risk
- Selenium detection risk
- challenge page detected

These cases are diagnosis-only. They do not access spiderbuf.cn, do not include private solutions, and do not include access-control defeat steps.

```powershell
python -m tools.validation.run_spiderbuf_inspired_validation
```

## Integrations

Collect Playwright test-results into a failure pack:

```powershell
failure-doctor collect-playwright .\examples\mock_playwright_test_results --out .\tmp_failure_pack
failure-doctor diagnose .\tmp_failure_pack --out .\tmp_collected_report
```

Normalize a loose log folder:

```powershell
failure-doctor pack-logs .\examples\mock_raw_logs --out .\tmp_log_pack
failure-doctor diagnose .\tmp_log_pack --out .\tmp_log_report
```

Normalize a Selenium, Puppeteer, Cypress, Scrapy, requests, or httpx failure log:

```powershell
failure-doctor adapt .\examples\cross_framework_fixtures\selenium\no_such_element\raw --framework selenium --out .\tmp_selenium_pack
failure-doctor diagnose .\tmp_selenium_pack --out .\tmp_selenium_report
failure-doctor plan .\tmp_selenium_report --out .\tmp_selenium_fix_plan
```

Supported adapter frameworks:

```text
selenium | puppeteer | cypress | scrapy | requests | httpx | auto
```

Playwright remains the deepest native trace backend. Cross-framework adapters normalize local logs and metadata into the same failure lifecycle; they do not run those frameworks or connect to external platforms.

See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) and [docs/GITHUB_ACTION_USAGE.md](docs/GITHUB_ACTION_USAGE.md).

## Validation Status

Current stable milestone: Agent Failure Doctor v2.5.0 AI Handoff & Patch Proposal Pack.

Latest added validation track: P95 Core Triad Gate.

- 131 source-ledger records with separated `real_public_issue`, `official_doc_pattern`, and `public_inspired_sanitized` labels
- 50 traceable real public issue records
- 100 Playwright Trace Doctor P95 fixtures
- 100/100 Playwright trace reasonable classifications
- 100/100 Playwright trace exact subtype matches
- 62 external public reference seeds
- 20 external public reference held-out records
- 20/20 external public reference reasonable classifications
- 20/20 external public reference actionable next actions
- 12 resolution validation cases
- 12/12 resolution statuses correct
- 18 applied scenario validation cases
- 18/18 applied scenario reasonable classifications
- 18/18 applied scenario valid fix plans
- 18/18 applied scenario verification statuses correct
- Playwright collector, generic log packer, browser-use adapter, and GitHub Actions usage docs
- v2.0 Auto Capture command wrapper: `failure-doctor run -- <command>`
- Sanitize & Share command: `failure-doctor sanitize <failed_run> --out <shareable_failure_pack>`
- Cross-framework adapter command: `failure-doctor adapt <input> --framework <framework> --out <failure_pack>`
- 100 cross-framework P95 fixtures across Selenium, Puppeteer, Cypress, Scrapy, requests, httpx, browser-use, and generic RPA
- 100/100 cross-framework P95 reasonable classifications
- 100/100 cross-framework P95 valid fix plans
- 0 forbidden outputs in cross-framework P95 validation
- 40 training challenge P95 local-only validation cases
- 40/40 training challenge reasonable classifications
- 40/40 training challenge valid fix plans
- 40/40 training challenge verification statuses correct
- 0 forbidden outputs and 0 private solution leaks in training challenge validation
- 160 composite P95 strict local-only validation cases
- 160/160 composite primary classifications correct
- 160/160 composite repair-order checks correct
- 160/160 composite evidence graphs generated
- 0 forbidden outputs in composite P95 strict validation
- P95 Core Triad Gate: pass
- 3 composite showcase reports under `sample_reports/composite_showcase/`
- 10 external held-out public-source records
- 9/10 external held-out reasonable classifications
- 10/10 external held-out actionable next actions
- 0 forbidden outputs in generated reports/prompts
- GitHub Actions green across Ubuntu, macOS, Windows, plus Windows benchmark/smoke/safety

See [docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md), [docs/EXTERNAL_DATA_SOURCES.md](docs/EXTERNAL_DATA_SOURCES.md), and [validation/dashboard.md](validation/dashboard.md) for validation metrics, limits, and boundaries.

## Reproduce Validation

```powershell
python -m tools.real_trace_generation.generate_real_trace_fixtures --out .\examples\realistic_playwright_traces --count 30 --clean
python -m tools.validation.run_real_trace_validation
python -m tools.validation.run_playwright_trace_p95_validation
python -m tools.validation.run_external_public_reference_validation
python -m tools.validation.run_resolution_validation
python -m tools.validation.run_spiderbuf_inspired_validation
python -m tools.validation.run_training_challenge_validation
python -m tools.validation.run_cross_framework_p95_validation
python -m tools.validation.run_composite_diagnosis_p95_strict_validation
python -m tools.validation.run_p95_core_triage_gate
python scripts\validate_external_heldout.py
```

## Safety Boundary

This project is for local, sanitized failure diagnosis.

It is not:

- a challenge-solving tool
- an access-control circumvention tool
- a credential extractor
- a real-platform scraper
- a tool for unauthorized collection

For suspected platform risk cases, the intended output is identification, routing, and compliance-oriented next steps such as reducing request volume, using an official API, confirming authorization, contacting the platform, or stopping unauthorized collection.

## Contributing Failure Cases

You do not need to write code. The most useful contribution is a sanitized failure case: log snippets, trace metadata, network summaries, screenshot metadata, and a short description of what happened.

Open an [External failure case issue](.github/ISSUE_TEMPLATE/external_failure_case.yml) and remove secrets before posting:

- passwords
- API keys
- cookies
- tokens
- authorization headers
- private screenshots
- private data
- personal data

Accepted input types include sanitized `error.log`, `trace.zip`, `console.txt`, `network.json`, screenshot metadata, and `user_description.txt`.

If you allow it, a sanitized case may be assigned an `EXT-YYYY-NNNN` id, run once with the current released version before rule changes, and added to the external validation dashboard. Templates and author-generated examples are not counted as external cases.

See [CONTRIBUTING.md](CONTRIBUTING.md), [docs/external_validation_protocol.md](docs/external_validation_protocol.md), [docs/REAL_TRACE_CONTRIBUTION_GUIDE.md](docs/REAL_TRACE_CONTRIBUTION_GUIDE.md), and [docs/REAL_DATA_SOURCES.md](docs/REAL_DATA_SOURCES.md).

## Commands

Run all tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Run smoke and safety checks:

```powershell
scripts\smoke_test.ps1
scripts\local_safety_scan.ps1
```
