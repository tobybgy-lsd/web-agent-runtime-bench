# Capability Dashboard (Sample)

*Public-safe excerpt from Phase 5.2-A2 bundle variant run.*

## Bundle Variant Failure Replay

| Variant | Error Type | Root Cause | Repair |
|---------|-----------|------------|--------|
| missing_window | missing_window | No shim loaded | Load synthetic_browser_shim.js |
| missing_document | missing_document | window defined, no document | Add document stub |
| missing_navigator | missing_navigator | shim partial, no navigator | Add navigator stub |
| missing_event_target | missing_event_target | shim partial, no EventTarget | Add EventTarget class |
| missing_local_storage | missing_local_storage | shim partial, no localStorage | Add localStorage stub |

## Full Shim Success

| Bundle | Shim Success | Mock API Accepted |
|--------|:---:|:---:|
| window_document | ✅ | ✅ |
| navigator | ✅ | ✅ |
| event_target | ✅ | ✅ |
| local_storage | ✅ | ✅ |
| full_runtime | ✅ | ✅ |

## Dependency Trace

Each `__warb_demo_sign()` call tracks 5 dependencies:
1. `path` — API path
2. `payload_hash` — SHA-256 of stable JSON payload
3. `user_agent` — navigator.userAgent
4. `local_salt` — localStorage.getItem("warb_demo_salt")
5. `algorithm` — WARBDemoV1 (SHA-256)

## Summary

- 5/5 runtime contract violations correctly detected
- 5/5 shim repairs successfully applied
- 5/5 mock API signature verifications passed
- 0 external network calls
- 0 real platform logic

## A3: Signed API Benchmark Dashboard

| Capability | Status |
|------------|:---:|
| matrix_bundle_loaded | PASS |
| cases_signed (6/6) | PASS |
| dependencies_traced | PASS |
| mock_api_verified (6/6) | PASS |
| negative_cases_rejected (6/6) | PASS |
| external_network_avoided | PASS |
| real_platform_logic_absent | PASS |
| synthetic_only | PASS |
