# KB Verified Fixes

A fix can be promoted only after a local verification report proves resolution:

```powershell
failure-doctor kb promote-fix --kb .\.failure-doctor-kb --case-id case_000001 --verification .\verification
```

Rules:

- verified fixes are suggestions, not auto-apply patches
- every suggestion requires human review
- unsafe cases cannot be promoted
- anti-bot boundary cases are routed to compliant next actions only
- verification commands are stored as redacted summaries
