# Failure Replay (Sample)

*Public-safe excerpt from Phase 5.2-A2 bundle variant run.*

## Failure #1: missing_window

```
Case: missing_window
Bundle: bundle_full_runtime_required.js
Entry: require('bundle_full_runtime_required.js');  (no shim)

Result: RC=1
Stderr: ReferenceError: window is not defined
Classifier: missing_window (confidence=0.93)

Repair: Load synthetic_browser_shim.js before bundle
Outcome: ✅ Full shim success, mock API accepted
```

## Failure #2: missing_document

```
Case: missing_document
Bundle: bundle_window_document_required.js
Entry: globalThis.window = globalThis; require('bundle_window_document_required.js');

Result: RC=1
Stderr: ReferenceError: document is not defined
Classifier: missing_document (confidence=0.93)

Repair: Add document stub to entry
Outcome: ✅ Full shim success, mock API accepted
```

## Failure #3: missing_navigator

```
Case: missing_navigator
Bundle: bundle_navigator_required.js
Entry: window + document + EventTarget + localStorage defined, no navigator

Result: RC=1
Stderr: ReferenceError: navigator is not defined
Classifier: missing_navigator (confidence=0.93)

Repair: Add navigator stub to entry
Outcome: ✅ Full shim success, mock API accepted
```

## Failure #4: missing_event_target

```
Case: missing_event_target
Bundle: bundle_event_target_required.js
Entry: window + document + navigator + localStorage defined, no EventTarget

Result: RC=1
Stderr: ReferenceError: EventTarget is not defined
Classifier: missing_event_target (confidence=0.93)

Repair: Add EventTarget class stub to entry
Outcome: ✅ Full shim success, mock API accepted
```

## Failure #5: missing_local_storage

```
Case: missing_local_storage
Bundle: bundle_local_storage_required.js
Entry: window + document + navigator + EventTarget defined, no localStorage

Result: RC=1
Stderr: ReferenceError: localStorage is not defined
Classifier: missing_local_storage (confidence=0.93)

Repair: Add localStorage stub to entry
Outcome: ✅ Full shim success, mock API accepted
```

## Root Cause Summary

All 5 failures share the same root cause: **browser globals absent in Node.js runtime**. The repair is uniform: load `synthetic_browser_shim.js` which provides IIFE-based stubs for window, document, navigator, EventTarget, and localStorage.

## A3: Signed API Benchmark Failure Replay

### Diagnostic Guide

1. **JS bundle not registered**: Check `window.__warb_demo_sign_matrix` exists after loading matrix bundle.
2. **Dependency missing**: Check `synthetic_browser_shim.js` is loaded before matrix bundle. Verify `navigator.userAgent`, `localStorage`, `document.querySelector` return expected synthetic values.
3. **Mock API rejected (accepted=false)**: Verify signature computation matches WARBDemoV2 algorithm on both JS and Python sides. Check key name alignment (e.g., `salt_source` not `salt`).
4. **Negative case not rejected**: Tampered payload hash must differ from original. Verify `stable_json` output is identical across JS and Python (sorted keys, no whitespace).

### Example: Salt Key Mismatch (fixed)

Root cause: JS bundle used `deps.salt` in seed string but dependency object had key `salt_source`. Fix: align key name to `salt_source`.

### Safety

All diagnostic steps are synthetic-only. No real platform debugging, no network access required.

