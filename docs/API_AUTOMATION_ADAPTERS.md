# API Automation Adapters

Agent Failure Doctor v4.4 supports local-only API automation artifacts such as
Postman/Newman reports and HTTP response bundles.

```powershell
failure-doctor adapter api normalize --input .\newman_report.json --out .\api_normalized
failure-doctor adapter api diagnose --input .\api_bundle --out .\api_report
```

For auth and rate-limit failures, reports should route to authorized
configuration checks, official quotas, SDKs, or export paths. They must not
recommend token theft, token guessing, proxy pools, or account pools.
