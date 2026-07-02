# CI in 10 Minutes

```powershell
failure-doctor ci run --input .\report --out .\ci_report --fail-on high
failure-doctor ci validate --input .\ci_report --out .\ci_validation
```
