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
python tools\warb.py pack `
  --tool playwright `
  --input path\to\failed_run `
  --out sample_run\failure_pack_001 `
  --run-id failure_pack_001 `
  --summary "Expected product page returned login form" `
  --status-code 200 `
  --required-field title `
  --required-field price
```

This creates:

- `failure_artifact.json`
- `diagnosis.md`
- `github_issue.md`
- `failure_pack.zip`

`warb pack` applies local text redaction rules for common tokens, cookies,
authorization headers, password fields, and session values. Review the generated
files before sharing them.

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
