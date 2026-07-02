# Backup and Restore

Backups are metadata-first by default. They record manifest information and
preserve audit-chain intent without copying raw traces, screenshots, secrets,
or private training artifacts.

```powershell
failure-doctor deploy backup --workspace .\.failure-doctor-enterprise --out .\backup
failure-doctor deploy restore --backup .\backup --out .\restored_workspace
```
