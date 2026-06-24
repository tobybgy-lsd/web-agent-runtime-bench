# Phase 5.2-A0: Synthetic Dynamic Runtime MVP Summary

**Date**: 2026-06-24
**Status**: PASS
**Tag**: phase5-2a-synthetic-dynamic-runtime-demo-v1

## Results

| Metric | Value |
|--------|-------|
| no_shim_run | failed (as expected) |
| classifier error_type | missing_window |
| with_shim_run | success |
| sign_function_resolved | true |
| dependency_count | 5 |
| mock_api_accepted | true |
| external_network | 0 |
| real_platform_logic | 0 |

## Design

1. `synthetic_obfuscated_bundle.js` — a synthetically obfuscated JS bundle that depends on browser globals (window, document, navigator, EventTarget, localStorage) and exports `__warb_demo_sign(path, payload)`.
2. Without shim, Node.js throws `ReferenceError: window is not defined`.
3. `runtime_error_classifier.py` identifies error_type = missing_window.
4. `synthetic_browser_shim.js` provides stubs for all 5 browser globals.
5. With shim loaded first, the bundle runs successfully.
6. `__warb_demo_sign("/local/mock/signed-api", payload)` computes a local SHA-256 signature.
7. `synthetic_signed_api.py` verifies the `x-demo-signature` header against the payload.

## Safety

All code is synthetic-only. No external network, no real platforms, no real signatures.
