# Phase 5.2 Synthetic Runtime Demo

## Prerequisites

- Python 3.10+
- Node.js 18+
- **No external network needed**
- **No API key required**
- **No cookie / authorization**
- **No real website access**

## Quickstart

### A0: Synthetic Dynamic Runtime MVP

```powershell
cd demo\phase5_2_runtime
python run_synthetic_runtime_demo.py --out-dir ..\..\sample_run\a0 --node node
```

This runs:
1. `synthetic_obfuscated_bundle.js` **without** browser shim → expected failure (missing_window)
2. Same bundle **with** `synthetic_browser_shim.js` → success
3. `__warb_demo_sign()` generates `x-demo-signature` header
4. `synthetic_signed_api.py` verifies the signature locally

### A2: Bundle Variants

```powershell
cd demo\phase5_2_runtime
python run_bundle_variant_cases.py --out-dir ..\..\sample_run\a2 --node node
```

This runs 10 cases (5 failure + 5 success) across 5 synthetic bundles:
- `bundle_window_document_required.js`
- `bundle_navigator_required.js`
- `bundle_event_target_required.js`
- `bundle_local_storage_required.js`
- `bundle_full_runtime_required.js`

## What is Synthetic?

All JS code is **locally generated mock** — no real websites, no real signatures, no real anti-bot systems. The `x-demo-signature` header is a local SHA-256 hash for benchmark purposes only.

## Expected Output

```
{
  "total_variants": ...,
  "classified_failures": ...,
  "full_shim_success_count": ...,
  "mock_api_accepted_count": ...,
  "external_network": 0,
  "real_platform_logic": 0,
  "overall_status": "PASS"
}
```
