# Agent Failure Doctor v5.0.0 - Stable API, Schema, and Plugin ABI

v5.0 locks the stable CLI command groups, schema registry, plugin ABI, backward
compatibility policy, deprecation policy, and migration guide.

## Install

```powershell
python -m pip install agent-failure-doctor
failure-doctor --help
failure-doctor stability check-api --out .\stability_report
```

## What changed

- Added stable API, schema, and plugin ABI checks.
- Added compatibility, deprecation, and migration reports.
- Rolled v4.4 adapter, v4.5 deployment hardening, and v4.6 adoption docs into the v5 stable line.

## Reproduce

```powershell
python -m unittest tests.test_v50_stability -b
python -m tools.validation.run_stable_api_schema_plugin_abi_validation
python -m tools.validation.run_p98_master_gate
```

## Safety

This release remains local-first, no-upload, no-telemetry, and diagnostic-only.
The P98 gate records forbidden output count as 0 across the stable validation pillars.

## Known limits

- Ecosystem maturity is excluded from the controlled maturity score.
- Anti-bot risk remains detection, compliant routing, and safe next action only.
