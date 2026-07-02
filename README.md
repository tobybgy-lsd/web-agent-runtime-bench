# Agent Failure Doctor

[中文文档](README.zh-CN.md)

![CI](https://github.com/tobybgy-lsd/web-agent-runtime-bench/actions/workflows/benchmark.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

Local-first failure diagnosis lifecycle tool for AI browser automation,
Playwright, crawler, RPA, and business automation failures.

**Input:** trace.zip / error.log / console.txt / network.json / probe_report.json / screenshot metadata / user_description.txt / visual_run / OCR or document evidence.

**Output:** diagnosis, evidence, next action, repair suggestions, GitHub issue draft, Codex fix prompt.

Quickstart: `python -m pip install agent-failure-doctor`; `git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git`; `cd web-agent-runtime-bench`; `failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report`; `failure-doctor plan .\report --out .\fix_plan`; `failure-doctor propose-patch --repo . --report .\report --out .\patch_plan`; `failure-doctor agent-bootstrap --target all --project .`.

**P98 gate:** passed. P98 master gate passed.
See [validation/dashboard.md](validation/dashboard.md) for the validation dashboard.
Earlier stable line: Agent Failure Doctor v3.9.0 Local Failure Knowledge Base Pack.
Previous P95 stable: v2.4.1.

**Lifecycle commands:** `diagnose` / `plan` / `verify` / `run`.

**Classic lifecycle:** diagnose -> plan -> AI handoff / patch proposal -> verify -> sanitize/share.

**Key commands:** `failure-doctor propose-patch`; `failure-doctor batch`; `sanitize` / `adapt`.

Optional v5.0 output: sanitized public cases, benchmark reports, adapter reports, deployment health reports, stability reports, plugin validation reports, evidence-bound reasoning, local web console, and CI/CD gate.

- Current milestone: Agent Failure Doctor v5.0 Stable API / Schema / Plugin ABI Standardization Release
- Current stable line: v5.0.0
- Previous stable line: Agent Failure Doctor v4.3.0 Real User Case Program & Public Benchmark Pack
- Previous stable line: Agent Failure Doctor v4.2.0 Plugin SDK & Adapter Ecosystem Pack
- Earlier stable line: Agent Failure Doctor v4.1.0 Enterprise Governance & Role-Based Console Pack
- Earlier stable line: Agent Failure Doctor v4.0.0 Hybrid Evidence Reasoning Pack
- Earlier stable line: Agent Failure Doctor v3.9.0 Local Failure Knowledge Base Pack (v3.9 Local Failure Knowledge Base Pack)
- Previous P95 stable line: Agent Failure Doctor v2.4.1 P95 Alignment & Missing Tracks Pack

**Classic lifecycle:** diagnose -> plan -> AI handoff / patch proposal -> verify -> sanitize/share.

**Patch command:** `failure-doctor propose-patch`.

**Share/adapt commands:** `sanitize` / `adapt`.

**Fleet command:** `failure-doctor batch`.

**Core commands:** `diagnose` / `plan` / `verify` / `run`; `case`; `issue-pack`; `benchmark`; `adapter`; `deploy`; `stability`; `plugin`; `reason` / `root-cause` / `causal-chain`; `agent-bootstrap`; `sanitize` / `adapt`; `ocr-evidence`; `visual-runtime`; `regulated-eval`; `full-chain-eval`; `console`; `ci`; `kb`; `failure-doctor propose-patch`; `failure-doctor batch`.

### v5.0 Stable Platform Commands

```powershell
failure-doctor adapter api diagnose --input .\newman_report.json --out .\api_report
failure-doctor deploy health --workspace .\.failure-doctor-enterprise --out .\health_report
failure-doctor stability check-api --out .\stability_report
```

v5.0 locks the stable CLI, schema registry, plugin ABI, benchmark case format,
public case manifest, and enterprise policy baseline. See
[docs/STABILITY_POLICY.md](docs/STABILITY_POLICY.md),
[docs/SCHEMA_REGISTRY.md](docs/SCHEMA_REGISTRY.md), and
[docs/PLUGIN_ABI_STABILITY.md](docs/PLUGIN_ABI_STABILITY.md).

### Real User Case Program & Public Benchmark

```powershell
failure-doctor case intake --input .\raw_failure_pack --out .\sanitized_case
failure-doctor case publish-check --case .\sanitized_case
failure-doctor issue-pack create --input .\raw_failure_pack --out .\issue_pack
failure-doctor benchmark run --suite public-safe --out .\benchmark_public
failure-doctor benchmark compare --baseline .\benchmark_public --candidate .\benchmark_public --out .\benchmark_compare
```

v4.3 adds a public-safe case intake path and deterministic benchmark runner.
Cases use `public_case/v1` manifests, sanitized inputs, expected diagnosis
metadata, and publish checks before anything is shared. Benchmarks run local
synthetic suites only and produce `benchmark_manifest.json`,
`benchmark_summary.md/json`, `case_results.jsonl`, `failures.md`,
`regression_diff.json`, and `open_this_first_benchmark.md`.

See [docs/REAL_USER_CASE_PROGRAM.md](docs/REAL_USER_CASE_PROGRAM.md),
[docs/CASE_CONTRIBUTION_GUIDE.md](docs/CASE_CONTRIBUTION_GUIDE.md),
[docs/PUBLIC_BENCHMARK_SPEC.md](docs/PUBLIC_BENCHMARK_SPEC.md), and
[docs/BENCHMARK_RUNNER.md](docs/BENCHMARK_RUNNER.md).

### Plugin SDK

```powershell
failure-doctor plugin scaffold --type framework-adapter --name toy_adapter --out .\plugins\toy_adapter
failure-doctor plugin validate .\plugins\toy_adapter
failure-doctor plugin install .\plugins\toy_adapter --workspace .\.failure-doctor-plugins
failure-doctor plugin enable toy_adapter --workspace .\.failure-doctor-plugins
failure-doctor plugin run toy_adapter --workspace .\.failure-doctor-plugins --input .\sample_artifacts --out .\plugin_report
```

The Plugin SDK lets teams extend Agent Failure Doctor with local-only framework
adapters, evidence adapters, diagnosis rule packs, industry packs, Console
extensions, CI extensions, KB patterns, reasoning tools, report exporters, and
validation packs.

Plugin safety rules:

- disabled by default
- manifest required
- permissions required
- local-only by default
- no upload by default
- no network by default
- no shell by default
- no raw evidence access by default
- safety gate and enterprise policy always apply
- plugin outputs are candidates; the core validator remains final authority

### Enterprise Governance

```powershell
failure-doctor enterprise init --workspace .\.failure-doctor-enterprise
failure-doctor enterprise user add --workspace .\.failure-doctor-enterprise --username alice --role developer
failure-doctor console --enterprise --workspace .\.failure-doctor-enterprise --open
```

Enterprise governance adds local users, role-based access control, approvals,
audit ledger, policy enforcement, project/team isolation, shared KB governance,
and sanitized audit exports. It remains local-only by default, binds to
`127.0.0.1` unless `--allow-lan` is explicit, requires local auth for enterprise
console mode, and does not enable cloud sync, telemetry, or external APIs.

Agent bootstrap: `failure-doctor agent-bootstrap --target all --project .`.

See [validation/dashboard.md](validation/dashboard.md).


## Quickstart

```powershell
python -m pip install agent-failure-doctor
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report `
  --auto-diagnose --auto-handoff --auto-sanitize
failure-doctor ocr-evidence extract --input .\screenshot.png --out .\ocr_report --provider mock_ocr
failure-doctor ocr-evidence compare --ocr .\ocr_report --dom .\dom_snapshot.html --out .\ocr_compare
failure-doctor visual-runtime diagnose --input .\visual_run --out .\visual_report --no-dom
failure-doctor visual-runtime compare --baseline .\dom_agent_run --candidate .\vlm_agent_run --out .\compare_report
failure-doctor regulated-eval --suite all --out .\regulated_report
failure-doctor full-chain-eval --input .\failed_run --out .\full_chain_report
failure-doctor console --import-report .\full_chain_report --open
failure-doctor ci run --input .\full_chain_report --out .\ci_report --fail-on high
failure-doctor ci templates --out .\ci_templates
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\full_chain_report
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --hybrid-reasoning --out .\report
failure-doctor reason --input .\report --out .\report\hybrid_reasoning
failure-doctor agent-bootstrap --target all --project .
```

### Hybrid Evidence Reasoning

v4.0 adds local, evidence-bound reasoning:

```powershell
failure-doctor reason --input .\report --out .\report\hybrid_reasoning
failure-doctor root-cause --input .\report --out .\root_cause_report
failure-doctor causal-chain --input .\report --out .\causal_chain_report
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --hybrid-reasoning --out .\report
```

The deterministic diagnosis remains the source of truth. Every reasoning claim
must cite a sanitized evidence id. Optional local reasoners never download
models automatically and never upload raw evidence.

### Local Failure Knowledge Base

v3.9 adds a local-only failure knowledge base:

```powershell
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report
failure-doctor kb search --kb .\.failure-doctor-kb --query "selector timeout after login redirect"
failure-doctor kb match --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report --out .\kb_match_report
failure-doctor kb export --kb .\.failure-doctor-kb --out .\kb_export --sanitized-only
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --out .\report
```

Use a local KB to match similar historical failures, reuse verified fix
candidates, and turn team troubleshooting history into a private, searchable
knowledge asset. The KB is local-only and sanitized-only by default: no cloud
sync, no external embedding API, no raw secret storage, no private local training
content, and verified fixes are suggestions, not auto-applied patches.

### CI/CD Integration

v3.8 adds local CI gates and starter templates:

```powershell
failure-doctor ci run --input .\report --out .\ci_report --fail-on high
failure-doctor ci validate --input .\ci_report --out .\ci_validation
failure-doctor ci templates --out .\ci_templates
```

The CI pack writes `ci_manifest.json`, `ci_summary.md/json`,
`severity_decision.json`, `gate_decision.json`, `audit_manifest.json`, and
`open_this_first_ci.md`. It is local-first, does not upload raw artifacts, and
blocks private training markers or unsafe recommendation markers before
external sharing. See [docs/CI_CD_INTEGRATION.md](docs/CI_CD_INTEGRATION.md).

### Local Web Console

v3.7 adds a local-only report console:

```powershell
failure-doctor console
failure-doctor console --host 127.0.0.1 --port 8765 --workspace .\.failure-doctor-console
failure-doctor console --import-report .\report --open
```

The console binds to `127.0.0.1` by default, serves bundled assets only, uses no
telemetry, requires a local token for POST actions, and hides raw local evidence
by default. It is a report viewer and workflow cockpit for diagnosis, evidence,
safety, AI handoff, patch proposal previews, visual runtime, OCR/document,
regulated workflow, batch/fleet, and full-chain reports. See
[docs/LOCAL_WEB_CONSOLE.md](docs/LOCAL_WEB_CONSOLE.md).

Release tracks: Current stable line: Agent Failure Doctor v4.3.0 Real User Case
Program & Public Benchmark Pack; previous stable line: Agent Failure Doctor
v4.2.0 Plugin SDK & Adapter Ecosystem Pack; previous P95 stable line:
Agent Failure Doctor v2.4.1 P95 Alignment & Missing Tracks Pack.

**Command groups:** diagnosis, repair planning, verification, collection, OCR evidence, visual runtime, patch proposal, fleet batch, and safe sharing.

Optional visual evidence: screenshot.png / dom_snapshot.html /
click_coordinates.json / ocr_excerpt.txt.

### Regulated Industry & Pure Visual Agent Evaluation

v3.6 adds local-only regulated workflow mock evaluation and full-chain agent
evaluation:

```powershell
failure-doctor regulated-eval --suite finance --out .\regulated_report
failure-doctor regulated-eval --suite government --out .\regulated_report
failure-doctor regulated-eval --suite healthcare --out .\regulated_report
failure-doctor regulated-eval --suite all --out .\regulated_report
failure-doctor full-chain-eval --input .\failed_run --out .\full_chain_report --include-safety --include-ocr --include-visual --include-regulated
```

These suites use synthetic local mock evidence only. They do not access real
finance, government, healthcare, patient, citizen, bank, or customer systems.
They are evidence-quality and shareability checks, not legal or regulatory
compliance advice.

### OCR & Document Evidence

Use OCR evidence for screenshots, PDFs, forms, tables, reports, RPA exports,
ecommerce SKU tables, ERP exports, and document-heavy automation failures.

```powershell
failure-doctor ocr-evidence extract --input .\screenshot.png --out .\ocr_report --provider mock_ocr
failure-doctor ocr-evidence compare --ocr .\ocr_report --dom .\dom_snapshot.html --out .\ocr_compare
failure-doctor ocr-evidence compare-vlm --ocr .\ocr_report --vlm .\vlm_responses.jsonl --out .\ocr_vlm_compare
```

Default provider is mock/local. No cloud OCR and no screenshot/PDF upload happen
by default. Cloud OCR requires explicit `--allow-cloud-ocr` and safety
evaluation. Sensitive documents are blocked or require sanitization. OCR
evidence is supporting evidence, not ground truth.

### Visual Agent Runtime Observability

`failure-doctor visual-runtime` diagnoses offline screenshot-driven agent runs:
screenshot capture, image payload cost, VLM observation metadata, action
grounding, coordinate clicks, DPR/viewport mapping, stale observations, OCR
semantics, and optional DOM/visual conflict.

It is local-only by default: no external VLM calls, no screenshot upload, no real
platform access, and no access-control defeat, identity-masking, protected
challenge automation, or behavior/pointer-path recipes.

```powershell
failure-doctor visual-runtime diagnose --input .\visual_run --out .\visual_report --no-dom
failure-doctor visual-runtime profile --input .\visual_run --out .\visual_profile
failure-doctor visual-runtime compare --baseline .\run_a --candidate .\run_b --out .\compare_report
failure-doctor visual-runtime adapt --source generic --input .\artifact_dir --out .\visual_run
failure-doctor visual-runtime validate --input .\visual_run --out .\validation_report
```

More docs: [docs/P98_LIMITS.md](docs/P98_LIMITS.md),
[docs/AGENT_FRONTEND_INVOCATION.md](docs/AGENT_FRONTEND_INVOCATION.md),
and [docs/safety_boundary.md](docs/safety_boundary.md).

P98 master gate passed with the safety compliance pillar included.

Advanced commands include `failure-doctor handoff`,
`failure-doctor agent-bootstrap`, `failure-doctor propose-patch`, and
`failure-doctor batch`.

**Core commands:** `collect` / `diagnose` / `plan` / `verify` / `run` /
`watch` / `sanitize` / `adapt` / `handoff` / `agent-bootstrap` /
`propose-patch` / `batch` / `visual-diagnose`

**Classic lifecycle:** `diagnose` / `plan` / `verify` / `run` /
`sanitize` / `adapt` -> `diagnose -> plan -> AI handoff / patch proposal
-> verify -> sanitize/share`

**P98 gate details:** `knowledge base -> coverage matrix ->
trace/cross-framework/training/composite/handoff/batch/sanitize/auto-collector
-> master gate`

## Distribution & Feedback

v4.3.0 is the current stable technical baseline. It adds public-safe case
intake, sanitized issue packs, and local benchmark/regression gates on top of
the local Plugin SDK, enterprise governance, hybrid evidence
reasoning, the local knowledge base, CI/CD gates, the local web console,
regulated-industry mock workflow evaluation, full-chain agent evaluation,
OCR/document evidence, offline visual runtime observability, and local-only
safety and compliance evaluation.

### Safety & Compliance Evaluation

```powershell
failure-doctor safety-evaluate --project . --out .\safety_report
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize --safety-evaluate
```

Safety boundary: local-only, evidence-only, no upload, and no active probe.
Safety boundary: no bypass challenges, no access-control evasion, no fingerprint
spoofing, no signature cracking, no challenge automation, and no private
remediation exposure.

- PyPI release runbook: [docs/PYPI_RELEASE.md](docs/PYPI_RELEASE.md)
- Active probe boundary: [docs/ACTIVE_PROBE_BOUNDARY.md](docs/ACTIVE_PROBE_BOUNDARY.md)
- Behavioral and Client Hints boundary:
  [docs/BEHAVIORAL_CLIENT_HINTS_BOUNDARY.md](docs/BEHAVIORAL_CLIENT_HINTS_BOUNDARY.md)
- JavaScript integrity boundary:
  [docs/JS_INTEGRITY_BOUNDARY.md](docs/JS_INTEGRITY_BOUNDARY.md)
- Canvas fingerprint boundary:
  [docs/CANVAS_FINGERPRINT_BOUNDARY.md](docs/CANVAS_FINGERPRINT_BOUNDARY.md)
- Visual and data-quality boundary:
  [docs/VISUAL_DATA_QUALITY_BOUNDARY.md](docs/VISUAL_DATA_QUALITY_BOUNDARY.md)
- 2-minute demo script: [docs/DEMO_VIDEO_SCRIPT.md](docs/DEMO_VIDEO_SCRIPT.md)
- Technical article draft: [docs/TECH_ARTICLE_DRAFT.md](docs/TECH_ARTICLE_DRAFT.md)
- Real user feedback loop: [docs/REAL_USER_FEEDBACK_LOOP.md](docs/REAL_USER_FEEDBACK_LOOP.md)

After PyPI publication, the target install command is:

```powershell
pip install agent-failure-doctor
```

For non-technical Windows users, double-click
`scripts/windows/Start-FailureDoctor-Diagnosis.bat` or drag a failed project
folder onto it.

Advanced v3.2 commands include `failure-doctor collect` and `failure-doctor watch`.

Advanced evidence inputs include `browser_runtime_report.json` and
`input_timing_summary.json`.
JavaScript/request-integrity evidence can be supplied as `js_integrity_report.json`.
Sanitized Canvas hash/session-count evidence can be supplied in
`browser_runtime_report.json`.

Agent frontend invocation:

```powershell
failure-doctor agent-bootstrap --target all --project .
```

This writes `.failure-doctor/AGENT_ENTRYPOINT.md` plus Codex, Cursor,
Claude Code, VS Code/Copilot, Antigravity, OpenCode, Qoder, Trae, WorkBuddy,
OpenClaw, Hermes, and generic agent workflow instructions.

Agent Failure Doctor uses a deterministic evidence-based diagnostic engine.
It does not claim to solve arbitrary failures, but it provides explainable
classification, evidence, fix plans, and before/after verification for known
automation failure patterns.

Applied scenario demos are local-only mock workflows for commerce automation,
live monitoring, content publishing, GUI data bridge, and ERP sync failure
diagnosis.

Spiderbuf-inspired challenge demos are local-only mock failure packs inspired
by public crawler-training challenge categories; they validate diagnosis and
safe next actions without accessing spiderbuf.cn or publishing private
remediation logic.

**Integration commands:** `failure-doctor collect-playwright` / `failure-doctor pack-logs` / `failure-doctor adapt`

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

Agent Failure Doctor turns sanitized automation failure materials into a report
that explains what likely failed, what evidence supports the diagnosis, what
evidence is missing, and what to ask Codex or another coding assistant to
change next.

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

This writes redacted logs, redacted network summaries, trace metadata only, a
redaction report, a review gate, and `shareable_failure_pack.zip`.

Raw `trace.zip` archives are not copied into the sanitized pack.

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

`verify` compares before/after evidence and reports whether the original failure
is resolved, unchanged, changed into another failure, or insufficiently
evidenced.

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

## Batch Diagnosis / Fleet Mode

Diagnose many failed runs and get a fleet-level summary:

```powershell
failure-doctor batch .\runs --out .\batch_report
```

Input:

```text
runs/
|-- run_001/
|-- run_002/
|-- run_003/
`-- ...
```

Output:

```text
batch_report/
|-- summary.json
|-- summary.md
|-- failures_by_type.csv
|-- top_root_causes.md
|-- repeated_failures.md
|-- suggested_regression_cases.md
|-- repair_priority.md
`-- reports/
```

Fleet mode answers which failures repeat, which root causes dominate, which runs
should become regression cases, and which fixes deserve priority.

## P98 Controlled Maturity

v3.0 starts the P98 controlled maturity track. This is not an ecosystem score;
it does not count stars, external PRs, external issues, PyPI downloads, or
long-term community adoption.

Current P98 assets:

- [docs/P98_CONTROLLED_MATURITY_SCORECARD.md](docs/P98_CONTROLLED_MATURITY_SCORECARD.md)
- [knowledge_base/](knowledge_base/)
- [docs/CRAWLER_FAILURE_COVERAGE_MATRIX.md](docs/CRAWLER_FAILURE_COVERAGE_MATRIX.md)
- [validation/crawler_failure_coverage_matrix.json](validation/crawler_failure_coverage_matrix.json)

Knowledge-base commands:

```powershell
python -m tools.knowledge_base.validate_patterns
python -m tools.knowledge_base.search_patterns --query selector_drift
python -m tools.validation.run_crawler_failure_coverage_matrix
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

These cases are diagnosis-only. They do not access spiderbuf.cn, do not include
private remediation details, and do not include access-control defeat steps.

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

Playwright remains the deepest native trace backend. Cross-framework adapters
normalize local logs and metadata into the same failure lifecycle; they do not
run those frameworks or connect to external platforms.

See [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) and [docs/GITHUB_ACTION_USAGE.md](docs/GITHUB_ACTION_USAGE.md).

## Validation Status

Current milestone: Agent Failure Doctor v4.3 Real User Case Program & Public Benchmark Pack.

Previous stable line: Agent Failure Doctor v4.2 Plugin SDK & Adapter Ecosystem Pack.

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
- 0 forbidden outputs and 0 private remediation leaks in training challenge validation
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

See [docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md),
[docs/EXTERNAL_DATA_SOURCES.md](docs/EXTERNAL_DATA_SOURCES.md), and
[validation/dashboard.md](validation/dashboard.md) for validation metrics,
limits, and boundaries.

## Reproduce Validation

```powershell
python -m tools.real_trace_generation.generate_real_trace_fixtures `
  --out .\examples\realistic_playwright_traces `
  --count 30 `
  --clean
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

For suspected platform risk cases, the intended output is identification,
routing, and compliance-oriented next steps such as reducing request volume,
using an official API, confirming authorization, contacting the platform, or
stopping unauthorized collection.

## Contributing Failure Cases

You do not need to write code. The most useful contribution is a sanitized
failure case: log snippets, trace metadata, network summaries, screenshot
metadata, and a short description of what happened.

Open an [External failure case issue](.github/ISSUE_TEMPLATE/external_failure_case.yml) and remove secrets before posting:

- passwords
- API keys
- cookies
- tokens
- authorization headers
- private screenshots
- private data
- personal data

Accepted input types include sanitized `error.log`, `trace.zip`, `console.txt`,
`network.json`, screenshot metadata, and `user_description.txt`.

If you allow it, a sanitized case may be assigned an `EXT-YYYY-NNNN` id, run
once with the current released version before rule changes, and added to the
external validation dashboard.

Templates and author-generated examples are not counted as external cases.

See [CONTRIBUTING.md](CONTRIBUTING.md),
[docs/external_validation_protocol.md](docs/external_validation_protocol.md),
[docs/REAL_TRACE_CONTRIBUTION_GUIDE.md](docs/REAL_TRACE_CONTRIBUTION_GUIDE.md),
and [docs/REAL_DATA_SOURCES.md](docs/REAL_DATA_SOURCES.md).

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

