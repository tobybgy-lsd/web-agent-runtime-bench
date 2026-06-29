# Agent Failure Doctor

[中文文档](README.zh-CN.md)

![CI](https://github.com/tobybgy-lsd/web-agent-runtime-bench/actions/workflows/benchmark.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Local-first failure diagnosis, repair planning, and fix verification for AI browser automation, Playwright, crawler, RPA, and business automation runs.

Input:
trace.zip / error.log / console.txt / network.json / screenshot metadata / user_description.txt

Output:
diagnosis, evidence, next action, repair suggestions, GitHub issue draft, Codex fix prompt.

Core commands:
`failure-doctor diagnose` / `failure-doctor plan` / `failure-doctor verify`

Applied scenario demos are local-only mock workflows for commerce automation, live monitoring, content publishing, GUI data bridge, and ERP sync failure diagnosis.

Integration commands:
`failure-doctor collect-playwright` / `failure-doctor pack-logs`

```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python -m pip install -e .
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

See [validation/dashboard.md](validation/dashboard.md) for release-level validation metrics and [validation/external_validation_dashboard.md](validation/external_validation_dashboard.md) for accepted external failure cases.

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

See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) and [docs/GITHUB_ACTION_USAGE.md](docs/GITHUB_ACTION_USAGE.md).

## Validation Status

Current milestone: Agent Failure Doctor v1.2 Integration Pack.

- 131 source-ledger records with separated `real_public_issue`, `official_doc_pattern`, and `public_inspired_sanitized` labels
- 50 traceable real public issue records
- 30 native Playwright-generated `trace.zip` fixtures
- 30/30 real trace reasonable classifications
- 30/30 real trace exact subtype matches
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
python -m tools.validation.run_external_public_reference_validation
python -m tools.validation.run_resolution_validation
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
