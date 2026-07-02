# Enterprise Deployment Hardening

Agent Failure Doctor v4.5 adds local deployment checks for enterprise
workspaces: health reports, metadata backups, restore validation, migration
dry-runs, retention plans, log rotation reports, offline bundles, disaster
recovery drills, and security posture reports.

```powershell
failure-doctor deploy health --workspace .\.failure-doctor-enterprise --out .\health_report
failure-doctor deploy backup --workspace .\.failure-doctor-enterprise --out .\backup
failure-doctor deploy offline-bundle --out .\offline_bundle
```

Deployment tooling is local-only and must not include user workspace data in
offline bundles.
