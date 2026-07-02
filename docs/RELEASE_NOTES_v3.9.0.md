# Agent Failure Doctor v3.9.0 - Local Failure Knowledge Base Pack

## Install

```powershell
python -m pip install agent-failure-doctor==3.9.0
failure-doctor kb --help
```

PyPI: https://pypi.org/project/agent-failure-doctor/

## Highlights

- Added `failure-doctor kb` for local failure knowledge bases.
- Added local case import, search, match, verified fix promotion, validation,
  sanitized export, and index rebuild commands.
- Added `diagnose --kb` and `ci diagnose --kb` historical case matching.
- Added local console KB read APIs and agent-bootstrap KB workflows.
- Added `local_failure_knowledge_base` to the P98 master gate.

## What changed

v3.9 turns one-off diagnosis reports into a private, searchable local history.
Teams can import sanitized reports, search similar failures, match a new report
against previous cases, and promote verified fixes only after local verification.

## Safety Boundary

The KB is local-only and sanitized-only by default. It does not use cloud sync
or external embedding APIs. It blocks raw secrets, private training artifacts,
and unsafe recommendations. Verified fixes are evidence-backed suggestions and
are never auto-applied.

Forbidden output count remains 0 in the validation ledger.

## Known limits

- Similarity matching is explainable token/fingerprint matching, not semantic
  omniscience.
- Verified fixes are not automatically applied.
- Private raw evidence and local-only training material are intentionally not
  exported.

## Reproduce

```powershell
python -m tools.validation.run_local_failure_kb_validation
python -m tools.validation.run_p98_master_gate
scripts\local_safety_scan.ps1
```

## Validation

- 160 local KB validation cases
- 100% blocked unsafe import behavior
- 100% sanitized export behavior
- 0 raw secrets in export
- 0 private local training material leaks
- 0 external API calls
