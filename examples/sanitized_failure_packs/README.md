# Sanitized Failure Pack Templates

These templates show the shape of realistic, public-safe failure packs that users can submit or adapt.

They are intentionally local and sanitized:

- no cookies, tokens, passwords, authorization headers, or real signatures
- no live endpoints or network replay requirements
- placeholder domains only
- short evidence files instead of full private dumps

Each directory contains:

- `failure_artifact.json` for `warb validate` and `warb diagnose`
- a short `README.md` explaining the failure
- sanitized evidence files referenced by the artifact

Use these as starting points when preparing a real failure pack for maintainers.

List available templates:

```powershell
python tools\warb.py template list
```

Copy one to an editable working directory:

```powershell
python tools\warb.py template copy playwright_selector_drift_product_card --out sample_run\my_failure_pack
```

Then edit the copied files and run the full pre-submit flow:

```powershell
python tools\warb.py flow sample_run\my_failure_pack --zip
```

If the flow reports `Flow status: ready`, it writes diagnosis outputs, a GitHub issue draft, and `failure_pack.zip`.

For step-by-step debugging, run the pieces individually:

```powershell
python tools\warb.py doctor sample_run\my_failure_pack
python tools\warb.py diagnose sample_run\my_failure_pack\failure_artifact.json --out-dir sample_run\my_failure_pack\diagnosis
python tools\warb.py issue sample_run\my_failure_pack
```
