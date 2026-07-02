# Enterprise Governance

Agent Failure Doctor v4.1 adds a local-only enterprise governance layer for
teams that need role-based access control, approvals, policy enforcement, audit
ledger records, shared KB governance, and sanitized audit exports.

```powershell
failure-doctor enterprise init --workspace .\.failure-doctor-enterprise
failure-doctor enterprise user add --workspace .\.failure-doctor-enterprise --username alice --role developer
failure-doctor enterprise validate --workspace .\.failure-doctor-enterprise
```

Defaults:

- local-only
- `127.0.0.1` by default
- `--allow-lan` explicit only
- local auth required for enterprise console mode
- no cloud sync
- no telemetry
- no external API by default
- sanitized export by default
- approval required for sensitive operations
- audit required

This is local mock compliance evaluation, not legal advice and not regulatory
certification.
