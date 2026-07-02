# Enterprise Policy Model

The default policy blocks raw access, disables cloud reasoners, disables
telemetry, keeps CI artifacts sanitized-only, requires audit logging, and keeps
patches proposal-only.

```powershell
failure-doctor enterprise policy list --workspace .\.failure-doctor-enterprise
failure-doctor enterprise policy set --workspace .\.failure-doctor-enterprise --policy .\enterprise_policy.yml
```
