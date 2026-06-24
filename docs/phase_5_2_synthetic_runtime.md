# Phase 5.2 Synthetic Runtime Benchmark

## A0: Runtime Demo MVP

- Node.js subprocess runs synthetic_obfuscated_bundle.js without shim
- Expected failure: ReferenceError (window is not defined)
- Classifier: identifies missing_window
- Repair: load synthetic_browser_shim.js before bundle
- Full shim: bundle exports window.__warb_demo_sign
- Mock API: verify x-demo-signature locally
- Result: PASS, external_network=0

## A1: Runtime Shim Variants

- 6 variant cases (missing_window/document/navigator/EventTarget/localStorage + full_shim)
- 3/5 classified by error type
- 2 unreachable (bundle did not actively reference navigator/EventTarget in A0)
- Full shim success and mock API accepted
- Effective PASS

## A2: Synthetic Bundle Variants

- 5 dedicated synthetic bundles, each requiring specific browser globals
- bundle_window_document_required.js
- bundle_navigator_required.js
- bundle_event_target_required.js
- bundle_local_storage_required.js
- bundle_full_runtime_required.js
- Results: 5/5 classified failures, 5/5 full shim success, 5/5 mock API accepted
- Overall PASS, external_network=0, real_platform_logic=0

## Safety

All bundles are synthetic-only. No real platform signatures (x-s, x-t, x-s-common). No network requests. No cookies or Authorization. Local mock API with x-demo-signature only.
