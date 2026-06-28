# Submit a Failure Pack

WebAgentRuntimeBench improves by turning real failures into sanitized synthetic regression cases. Please submit only artifacts you are allowed to share.

## What to Include

Start from one of the templates in `examples/sanitized_failure_packs/` when possible:

- `playwright_selector_drift_product_card/`
- `playwright_auth_expired_login_page/`
- `scrapy_rate_limit_soft_block/`

List and copy templates with the CLI:

```powershell
python tools\warb.py template list
python tools\warb.py template copy playwright_selector_drift_product_card --out sample_run\my_failure_pack
```

After editing the copied files, run the full pre-submit flow:

```powershell
python tools\warb.py flow sample_run\my_failure_pack --zip
```

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
python tools\warb.py flow sample_run\failure_pack_001 --zip
```

If you need to run each step manually:

```powershell
python tools\warb.py doctor sample_run\failure_pack_001
python tools\warb.py validate sample_run\failure_pack_001\failure_artifact.json
python tools\warb.py diagnose sample_run\failure_pack_001\failure_artifact.json --out-dir sample_run\failure_pack_001\diagnosis
python tools\warb.py issue sample_run\failure_pack_001
```

## What You Get Back

For useful submissions, maintainers can return:

- `diagnosis_report.md`
- likely failure type
- evidence and confidence
- suggested fix direction
- sanitized synthetic regression case when appropriate
