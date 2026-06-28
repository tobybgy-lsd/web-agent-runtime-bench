# Agent Failure Doctor

Diagnose why AI-generated browser automation / crawler / RPA runs failed.

Input:
trace.zip / error.log / console.txt / network.json / screenshot metadata / user_description.txt

Output:
diagnosis, evidence, next action, repair suggestions, Codex fix prompt.

```powershell
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench.git
cd web-agent-runtime-bench
python -m failure_doctor diagnose .\examples\failed_runs\proxy_failed --out .\report
```

Agent Failure Doctor is local-first. It turns sanitized automation failure
materials into a report that explains what likely failed, what evidence supports
the diagnosis, what evidence is missing, and what to ask Codex or another coding
assistant to change next.

## What You Get

```text
report/
├── diagnosis.json
├── diagnosis.md
├── evidence.json
├── input_summary.json
├── issue_draft.md
├── repair_suggestions.md
├── codex_fix_prompt.md
└── failure_doctor_report.zip
```

## One-Minute Start

Put a failed run in a folder:

```text
my_failed_run/
├── error.log
├── console.txt
├── network.json
├── README.txt
└── screenshot.png
```

Then run:

```powershell
python -m failure_doctor diagnose .\my_failed_run --out .\report
```

The tool automatically inventories inputs and uses this evidence priority:

```text
trace.zip > log > network.json > user description > screenshot metadata
```

When evidence is too thin, it should downgrade to `insufficient_evidence`
instead of guessing.

## Minimal Demos

Proxy/network failure:

```powershell
python -m failure_doctor diagnose .\examples\failed_runs\proxy_failed --out .\report_proxy
```

Strict mode locator conflict:

```powershell
python -m failure_doctor diagnose .\examples\failed_runs\strict_mode_locator --out .\report_locator
```

Low-evidence screenshot-only run:

```powershell
python -m failure_doctor diagnose .\examples\failed_runs\low_evidence_screenshot_only --out .\report_low_evidence
```

## Before / After Report

Report structure: 结论 / 证据 / 为什么 / 下一步 / 给 Codex 的修复指令

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

## Validation Status

Current public release: Agent Failure Doctor v0.4.0.

- 150 public-inspired sanitized validation records
- 100 public failure corpus cases
- 86.7% reasonable classification in the validation ledger
- 94% actionable `next_action`
- 160 tests
- smoke test and local safety scan passing

See [docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md) for the validation
ledger, limits, and current boundaries.

## Safety Boundary

This project is for local, sanitized failure diagnosis.

It is not:

- a CAPTCHA bypass tool
- a bot evasion tool
- a credential extractor
- a real-platform scraper
- a tool for unauthorized collection

For suspected anti-bot or platform risk cases, the intended output is
identification, routing, and compliance-oriented next steps such as reducing
request volume, using an official API, confirming authorization, contacting the
platform, or stopping unauthorized collection.

## Contributing Failure Cases

You do not need to write code. The most useful contribution is a sanitized
failure case: log snippets, trace metadata, network summaries, screenshots
metadata, and a short description of what happened.

Open a Failure case issue and remove secrets before posting:

- passwords
- API keys
- cookies
- tokens
- authorization headers
- private screenshots
- personal data

See [CONTRIBUTING.md](CONTRIBUTING.md) for the minimal contribution format.

## Commands

Run all tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Run smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
```

Run local safety scan:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```
