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

## A3: Synthetic Signed API Benchmark

- 6 signed API cases with increasing dependency complexity
- Dependencies: method, path, payload, timestamp, nonce, userAgent, localStorage salt, document meta token, event token
- Signature algorithm: WARBDemoV2 (SHA-256 over ordered seed string)
- Each case verified against locally computed expectation
- Each case tested with tampered-payload negative (must be rejected)
- Results: 6/6 signed, 6/6 verified, 6/6 negative rejected
- Dependency range: 3–9
- Overall PASS, external_network=0, real_platform_logic=0

### A3 Cases

| Case | Dependencies | Count |
|------|-------------|:---:|
| path_payload_basic | method, path, payload | 3 |
| timestamp_nonce | +timestamp, +nonce | 5 |
| user_agent_salt | +userAgent, +localStorage salt | 5 |
| document_meta_token | +document meta token | 4 |
| event_token | +synthetic event token | 4 |
| full_dependency_matrix | all 9 dependencies | 9 |

## Safety

All bundles are synthetic-only. No real platform signatures (x-s, x-t, x-s-common). No network requests. No cookies or Authorization. Local mock API with x-demo-signature only.
