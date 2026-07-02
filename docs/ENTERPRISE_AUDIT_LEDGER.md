# Enterprise Audit Ledger

Sensitive enterprise operations append local audit events. Each event includes a
hash pointer to the previous event so the local ledger can detect accidental
tampering.

```powershell
failure-doctor enterprise audit export --workspace .\.failure-doctor-enterprise --out .\audit_export --sanitized-only
```
