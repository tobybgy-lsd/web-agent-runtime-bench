# From Automation Failure Logs to AI Repair Task Packs

Agent Failure Doctor is a local-first failure diagnosis backend for Playwright,
crawler, RPA, AI browser automation, and business workflow failure reports.

The core idea is simple:

```text
failed run evidence -> diagnosis -> fix plan -> AI handoff -> verify -> sanitize
```

## Why This Exists

AI agents and automation scripts often fail with noisy logs:

- a selector timed out
- a request returned 403 or 429
- a browser context lost login state
- a mock route did not intercept a request
- a Docker or proxy environment broke

Opening raw logs is slow. Asking an AI assistant to repair code without a
diagnosis is also risky because it may chase the loudest symptom instead of the
root cause.

Agent Failure Doctor turns local evidence into an evidence-backed repair task.

## Auto Collector

The Auto Collector scans only the project folder selected by the user. It looks
for local failure evidence such as logs, Playwright traces, network summaries,
screenshots metadata, test reports, and framework-specific artifacts.

It skips dependency folders, Git internals, virtual environments, browser
profiles, SSH material, and credential stores.

```powershell
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report `
  --auto-diagnose --auto-handoff --auto-sanitize
```

## Evidence-based Diagnosis

The diagnosis engine is deterministic and explainable. It maps evidence into
known failure patterns such as:

- storage state / browser context mismatch
- route, mock, or HAR interception failure
- selector drift
- shadow DOM locator issue
- proxy, DNS, or TLS failure
- website change
- platform-risk boundary
- insufficient evidence

Each report includes the category, evidence, confidence, missing evidence, and
the next action.

## Repair Order

The fix plan tells an engineer or AI coding assistant what to change first and
what not to change.

This matters because many automation failures are composite. A platform-risk
block can create downstream selector timeouts; a proxy failure can create page
load failures; a login redirect can make every later locator fail.

## AI Handoff

The AI Handoff pack converts a diagnosis into instructions for tools such as
Codex, Cursor, Claude Code, VS Code/Copilot, Antigravity, OpenCode, Qoder, Trae,
WorkBuddy, OpenClaw, Hermes, and generic agent frontends.

The pack includes:

- diagnosis summary
- evidence
- repair plan
- allowed commands
- forbidden actions
- safety boundary
- verification steps

## Verify

After a repair, `failure-doctor verify` compares before/after evidence:

```powershell
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verification
```

The result should answer:

- was the original failure resolved?
- did it remain unchanged?
- did it become a different failure?
- is the evidence still insufficient?

## Safety Boundary

Agent Failure Doctor is not a CAPTCHA bypass tool, bot-evasion toolkit,
credential extractor, or unauthorized scraper.

For platform-risk cases, it provides identification, safe routing, and
compliance-oriented next actions such as confirming authorization, using an
official API, contacting the platform owner, or stopping unclear automation.

## P98 Gate

The v3.2.0 release includes a machine-checked P98 controlled maturity gate. It
measures local, controllable maturity: diagnosis coverage, validation assets,
safety boundaries, auto collection, AI handoff, and regression checks.

It does not count ecosystem maturity such as stars, downloads, community issues,
third-party integrations, or production adoption.

## What Comes Next

The next useful signal is not more synthetic cases. It is real, sanitized
failure reports from users.

If you have one, submit an External Failure Case issue with sanitized logs,
trace metadata, network summaries, or a short failure description.
