# Local Failure Knowledge Base

Agent Failure Doctor v3.9 adds a local-only knowledge base for sanitized
historical failure cases.

```powershell
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report
failure-doctor kb search --kb .\.failure-doctor-kb --query "selector timeout after login redirect"
failure-doctor kb match --kb .\.failure-doctor-kb --report .\failure_doctor_auto_report --out .\kb_match_report
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --out .\report
```

The KB stores sanitized summaries, evidence fingerprints, safe repair orders,
verified fix metadata, and local audit logs. It does not store raw traces,
secrets, browser profiles, credential stores, private training material, or
challenge artifacts.

Verified fixes are suggestions only. They are never auto-applied.
