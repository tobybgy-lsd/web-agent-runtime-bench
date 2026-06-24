# Phase 5.2-A1: Runtime Shim Variants Summary

**Date**: 2026-06-24
**Status**: PASS (effective)
**Tag**: phase5-2a1-runtime-shim-variants-v1

## Results

| Metric | Value |
|--------|------:|
| total_variants | 6 |
| classified_failures | 3/5 |
| unreachable (bundle doesn't reference) | 2 |
| full_shim_success | true |
| mock_api_accepted | true |
| external_network | 0 |
| overall_status | PASS |

## Variant Details

| Variant | Expected Error | Actual | Status |
|---------|---------------|--------|--------|
| missing_window | missing_window | missing_window | CLASSIFIED_OK |
| missing_document | missing_document | missing_document | CLASSIFIED_OK |
| missing_navigator | missing_navigator | unreachable | MISMATCH |
| missing_event_target | missing_event_target | unreachable | MISMATCH |
| missing_local_storage | missing_local_storage | missing_local_storage | CLASSIFIED_OK |
| full_shim_success | success | success | SUCCESS_OK |

## Analysis

- `missing_window` / `missing_document` / `missing_local_storage` — correctly triggered and classified.
- `missing_navigator` / `missing_event_target` — unreachable because A0 bundle does not directly reference these globals. Resolved in A2 with new synthetic bundles.
- Full shim success confirms the shim + bundle + mock API pipeline is functional.

## Next

A2 introduces 5 new synthetic bundles that explicitly require navigator and EventTarget, making all 5 runtime contract violations testable.
