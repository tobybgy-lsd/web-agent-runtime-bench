# One-Click Diagnosis

v3.2.0 includes Windows launchers for non-technical users.

```text
scripts/windows/Start-FailureDoctor-Diagnosis.bat
scripts/windows/Start-FailureDoctor-Diagnosis.ps1
```

You can double-click the BAT from a project folder, or drag a failed project folder onto it. The launcher runs:

```powershell
failure-doctor collect --project <folder> --preset auto --out <folder>\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize --open-report
```

The PowerShell launcher asks for confirmation and explains the safety boundary before collecting anything.

If `failure-doctor` is missing, install the local package first:

```powershell
python -m pip install -e .
```
