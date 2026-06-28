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

Current templates cover:

- `selector_drift`: stale product-card selector after page redesign
- `auth_expiry`: HTTP 200 login page after session expiry
- `rate_limit_or_soft_block`: HTTP 429 / soft-block response
- `network_http_error`: navigation timeout before usable response
- `async_hydration_timing`: extraction before client-side hydration
- `captcha_or_bot_wall`: human-verification challenge page
- `runtime_api_missing`: browser runtime API missing in Node
- `response_shape_change`: required fields missing or typed differently
- `js_bundle_obfuscation`: parser coupled to changed obfuscated bundle internals
- `playwright_strict_mode_violation`: locator matched multiple elements
- `playwright_frame_locator`: iframe/frame locator failed or frame attached late
- `playwright_file_chooser`: upload flow missed file chooser or file input
- `playwright_download`: download event/saveAs/acceptDownloads issue
- `playwright_popup`: popup/new-page flow was not awaited or wrong page used
- `playwright_service_worker_cache`: stale cached response from service worker/cache storage
- `playwright_storage_state_context`: storageState/browser context mismatch, including cookie domain, missing state, recreated context, missing localStorage, and baseURL/origin mismatch
- `playwright_route_mock_har`: route/mock/HAR interception failures, including pattern mismatch, late registration, missing HAR, fallback network leaks, and mock response shape mismatch

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
