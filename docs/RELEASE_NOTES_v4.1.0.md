# Agent Failure Doctor v4.1.0 - Enterprise Governance & Role-Based Console Pack

v4.1.0 adds local enterprise governance: workspace initialization, local users,
RBAC roles, policy checks, approval requests, audit ledger exports, console
status integration, CI policy integration, and agent-bootstrap governance
instructions.

## Install

```powershell
python -m pip install agent-failure-doctor
failure-doctor enterprise --help
```

PyPI: https://pypi.org/project/agent-failure-doctor/

## Highlights

- local enterprise workspace
- role-based access control
- approval workflow for sensitive actions
- append-only audit ledger with hash-chain validation
- sanitized audit export
- enterprise console status
- enterprise CI audit reference
- P98 pillars for enterprise governance, role-based console, and audit ledger

## What changed

- Added `failure-doctor enterprise init/user/role/policy/request/approve/audit/validate/report`.
- Added enterprise-aware console status and `ci diagnose --enterprise-workspace`.
- Added agent-bootstrap governance workflow files for supported AI frontends.
- Added validation output at `validation/enterprise_governance_validation.json`.

## Safety

Defaults remain local-only: no cloud sync, no telemetry, no external API calls,
sanitized exports by default, raw access blocked by default, and patch auto-apply
unavailable.

Forbidden output count is expected to remain 0 across the P98 gate.

## Reproduce

```powershell
python -m tools.validation.run_enterprise_governance_validation
python -m tools.validation.run_p98_master_gate
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

## Known limits

- This is local mock compliance evaluation, not legal advice and not regulatory certification.
- Enterprise policies are local JSON policy checks, not a replacement for a corporate IAM system.
- Approval records and audit exports are generated locally and should be reviewed before sharing.

This is local mock compliance evaluation, not legal advice and not regulatory
certification.
