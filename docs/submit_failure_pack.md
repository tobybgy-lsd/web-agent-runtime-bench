# Submit a Failure Pack

WebAgentRuntimeBench improves by turning real failures into sanitized synthetic regression cases. Please submit only artifacts you are allowed to share.

## What to Include

Create a local directory with any of these files:

```text
error.log
snapshot.html
screenshot.png
network.json
console.log
expected_schema.json
actual_output.json
notes.md
```

Do not include:

- cookies
- tokens
- passwords
- authorization headers
- private customer data
- real platform signature secrets

## Package the Artifact

```powershell
python tools\warb.py collect `
  --input path\to\sanitized_failure `
  --out sample_run\failure_pack_001 `
  --run-id failure_pack_001 `
  --tool playwright `
  --summary "Expected product page returned login form" `
  --error-message "Timeout waiting for selector .price" `
  --status-code 200 `
  --failure-type auth_expiry `
  --label-confidence 0.8 `
  --required-field title `
  --required-field price `
  --sanitized `
  --redaction-notes "Host, account, and credentials removed."
```

Validate it:

```powershell
python tools\warb.py validate sample_run\failure_pack_001\failure_artifact.json
```

Generate a diagnosis report:

```powershell
python tools\warb.py diagnose sample_run\failure_pack_001\failure_artifact.json --out-dir sample_run\failure_pack_001\diagnosis
```

## What You Get Back

For useful submissions, maintainers can return:

- `diagnosis_report.md`
- likely failure type
- evidence and confidence
- suggested fix direction
- sanitized synthetic regression case when appropriate
