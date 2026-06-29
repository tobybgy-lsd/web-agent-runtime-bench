# Content Publishing Workflow Failure Diagnosis

Diagnoses local-only authorized content workflow failures around iframes, uploads, and permission/manual approval gates.

This is a local-only mock failure diagnosis demo. It is not a production business automation system and does not connect to real platforms.

Run the primary case:

```powershell
failure-doctor diagnose .\failed_run --out .\tmp_report
failure-doctor plan .\tmp_report --out .\tmp_plan
failure-doctor verify --before .\failed_run --after .\rerun_after_fix --out .\tmp_verify
```
