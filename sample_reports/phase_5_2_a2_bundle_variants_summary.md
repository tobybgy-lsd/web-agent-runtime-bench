# Phase 5.2-A2: Synthetic Bundle Variants Summary

**Date**: 2026-06-24
**Status**: PASS
**Tag**: phase5-2a2-synthetic-bundle-variants-v1

## Results

| Metric | Value |
|--------|------:|
| failure_cases | 5 |
| classified_failures | 5 |
| unknown_errors | 0 |
| success_cases | 5 |
| full_shim_success_count | 5 |
| mock_api_accepted_count | 5 |
| external_network | 0 |
| real_platform_logic | 0 |
| overall_status | PASS |

## Failure Cases

| Case | Bundle | Expected Error | Actual | Status |
|------|--------|---------------|--------|--------|
| missing_window | full_runtime | missing_window | missing_window | OK |
| missing_document | window_document | missing_document | missing_document | OK |
| missing_navigator | navigator | missing_navigator | missing_navigator | OK |
| missing_event_target | event_target | missing_event_target | missing_event_target | OK |
| missing_local_storage | local_storage | missing_local_storage | missing_local_storage | OK |

## New Synthetic Bundles

| Bundle | Required Globals |
|--------|-----------------|
| bundle_window_document_required.js | window, document |
| bundle_navigator_required.js | navigator.userAgent |
| bundle_event_target_required.js | EventTarget |
| bundle_local_storage_required.js | localStorage |
| bundle_full_runtime_required.js | window, document, navigator, EventTarget, localStorage |

## Classifier Fix

The runtime error classifier was updated to use precise pattern matching (`xxx is not defined`) for each browser global, resolving the A1 issue where navigator and EventTarget were unreachable.
