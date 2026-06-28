# Failure Classifier Coverage

`warb diagnose` is a local, rule-based triage layer. It is designed to separate
common web automation failure categories before a developer or coding assistant
starts changing scraper code.

## Covered Types

| Failure type | MVP evidence | Fix direction |
|---|---|---|
| `runtime_api_missing` | `window/document/navigator/localStorage/EventTarget` reference errors | Add a browser shim or run in a browser context |
| `network_http_error` | 401/403/5xx, timeout, DNS, connection reset, TLS-style transport text | Separate transport failure from parser/selector changes |
| `rate_limit_or_soft_block` | 429 or 200 body containing rate-limit / soft-block text with empty output | Backoff or authorized retry; no evasion logic |
| `response_shape_change` | Required fields missing, empty arrays, type-change markers | Diff expected schema against actual output |
| `selector_drift` | Selector timeout, missing selectors, missing fields after selector lookup | Compare DOM snapshot with selector assumptions |
| `async_hydration_timing` | Hydration markers, short network-idle window, DOM mutation after failure | Wait for semantic readiness before extraction |
| `auth_expiry` | Password/login/session-expired markers or login redirects | Refresh session and add login-state preflight |
| `captcha_or_bot_wall` | CAPTCHA, challenge, human verification markers | Stop and request authorized/manual review |
| `js_bundle_obfuscation` | eval/webpack/dynamic-function markers plus missing exports | Treat as bundle contract change, not selector drift |
| `toolchain_environment` | Missing local runtime, permission, path, module errors | Fix local environment and rerun smoke tests |

## Covered Playwright Fine Types

These are narrower Playwright failure modes recognized in addition to the broad
web automation categories above:

| Failure type | MVP evidence | Fix direction |
|---|---|---|
| `playwright_strict_mode_violation` | strict-mode or multiple-match locator errors | Narrow locator scope to one intended element |
| `playwright_frame_locator` | `frameLocator`, iframe, detached frame, or missing-frame markers | Wait for and scope into the correct frame |
| `playwright_file_chooser` | file chooser, upload, or `setInputFiles` markers | Await the chooser and verify local file path/input state |
| `playwright_download` | download event, `acceptDownloads`, `saveAs`, or suggested filename markers | Wait for the download and persist before context close |
| `playwright_popup` | popup/new-page event markers | Wait for the popup and continue extraction on the new page |
| `playwright_service_worker_cache` | service-worker/cache-source markers such as `fromServiceWorker` | Separate stale cache/state from parser or selector bugs |
| `playwright_storage_state_context` | storageState/context markers, missing cookies/storage, login redirects after state reuse | Align storageState, baseURL, cookies, and browser context lifecycle |
| `playwright_route_mock_har` | route/mock/HAR markers, route misses, fallback network leaks, mock schema mismatch | Fix route patterns, registration timing, HAR loading, and mock contracts |

## Adapters

`warb adapt` converts captured evidence into `failure_artifact.json`:

```bash
python tools/warb.py adapt playwright-trace trace.zip --out sample_run/from_trace --diagnose
python tools/warb.py adapt scrapy scrapy.log --response response.html --out sample_run/from_scrapy
python tools/warb.py adapt requests requests_capture.json --out sample_run/from_requests
```

Adapters do not replay network traffic. They only normalize local, already
captured evidence.

The Playwright trace adapter extracts bounded action-level evidence from
synthetic/local trace records, including failed action metadata, exception
details, network summaries, snapshot references, linked DOM excerpts, and
selector hints such as missing selectors plus nearby candidate classes/text. It
also preserves Playwright-specific action events and response source metadata
used by the fine-type classifiers, such as `filechooser`, `download`, `popup`,
and `fromServiceWorker`.

## Regression Fixtures

Generate a metadata-only synthetic fixture from a sanitized pack:

```bash
python tools/warb.py regression generate sample_run/failure_pack_001 --out failure_corpus/synthetic
```

Generated fixtures do not include credentials, external network calls, or real
platform bypass logic.

## Current Limits

These are MVP heuristics, not a production classifier trained on a large corpus.
Classifier weights should be calibrated with real sanitized failure packs.
