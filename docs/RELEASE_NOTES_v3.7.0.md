# Agent Failure Doctor v3.7.0 - Local Web Console Pack

## Install

```powershell
python -m pip install agent-failure-doctor
failure-doctor --help
```

PyPI: https://pypi.org/project/agent-failure-doctor/

## What changed

- Added `failure-doctor console`.
- Added a local-only report dashboard for diagnosis, evidence, safety, AI
  handoff, patch proposal previews, visual runtime, OCR/document, regulated
  workflow, batch/fleet, and full-chain evaluation reports.
- Added workspace-scoped report import and audit log.
- Added local token protection for POST routes.
- Added bundled CSS/JavaScript only; no CDN and no telemetry.
- Added `local_web_console_validation.json` with 96 local validation cases.
- Added `local_web_console` to the P98 master gate.

## Reproduce

```powershell
python -m unittest discover
python -m tools.validation.run_local_web_console_validation
python -m tools.validation.run_p98_master_gate
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

## Safety Boundary

The console is a local report viewer. It does not upload evidence, call remote
AI/VLM/OCR services, expose raw local-only evidence, apply patches, or publish
private training solutions. Shareable artifacts should come from sanitized
packs.

Forbidden outputs remain blocked: no private solver code, no raw secrets, no
real-platform access, and no guidance for bypass or evasion.

## Known limits

- The console is a local report viewer, not a hosted service.
- Patch proposal pages are read-only previews.
- Missing report sections are shown as unavailable.
- LAN binding requires explicit `--allow-lan`.
