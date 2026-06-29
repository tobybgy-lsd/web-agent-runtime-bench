# Applied Scenario Demos

These local-only mock demos show how Agent Failure Doctor diagnoses failures in business automation style workflows. They are not a production commerce, content, GUI, or ERP system.

Each scenario uses sanitized files only and runs through:

```powershell
failure-doctor diagnose <failed_run> --out <report>
failure-doctor plan <report> --out <fix_plan>
failure-doctor verify --before <failed_run> --after <rerun_after_fix> --out <verification>
```

The demos do not connect to real platforms, do not include credentials, and do not provide platform-risk circumvention guidance.
