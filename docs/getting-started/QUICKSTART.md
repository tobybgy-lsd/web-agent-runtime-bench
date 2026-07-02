# Quickstart

```powershell
python -m pip install agent-failure-doctor
failure-doctor diagnose .\failed_run --out .\report
failure-doctor plan .\report --out .\fix_plan
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\verify
```
