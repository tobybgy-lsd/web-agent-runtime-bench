# CI/CD Integration Example

This folder documents the v3.8 local CI flow.

```powershell
failure-doctor diagnose .\my_failed_run --out .failure-doctor\report
failure-doctor ci run --input .failure-doctor\report --out .failure-doctor\ci --fail-on high
failure-doctor ci templates --out .failure-doctor\templates
```

The CI command writes a local report and gate decision. It is intended for sanitized, local artifacts only.
