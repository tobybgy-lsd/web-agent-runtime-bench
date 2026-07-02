# Enterprise CI Governance

CI can attach enterprise policy and audit references:

```powershell
failure-doctor ci diagnose --project . --enterprise-workspace .\.failure-doctor-enterprise --out .\ci_report
```

CI summaries remain sanitized-only and record the enterprise audit reference.
