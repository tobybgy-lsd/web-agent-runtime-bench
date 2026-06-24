# Runtime Diagnosis Patterns

Synthetic runtime failure patterns for WebAgentRuntimeBench. All patterns are **local/synthetic only**. Not real-platform bypass methods.

## Pattern Reference

| Pattern | Likely Cause | Classifier Output | Fix Strategy | Related Demo |
|---------|-------------|-------------------|-------------|-------------|
| `ReferenceError: window is not defined` | No browser shim loaded before bundle | `missing_window` | Load `synthetic_browser_shim.js` before bundle | A0, A2 |
| `ReferenceError: document is not defined` | `window` defined but no `document` object | `missing_document` | Add document stub with `querySelector`, `createElement` | A1, A2 |
| `ReferenceError: navigator is not defined` | `window` + `document` defined but no `navigator` | `missing_navigator` | Add navigator stub with `userAgent` | A1, A2 |
| `ReferenceError: localStorage is not defined` | Other globals present but no `localStorage` | `missing_local_storage` | Add localStorage stub with `getItem`/`setItem` | A1, A2 |
| `ReferenceError: EventTarget is not defined` | Other globals present but no `EventTarget` | `missing_event_target` | Define SyntheticEventTarget class | A1, A2 |
| Bundle exports undefined | Bundle loaded but `window.__warb_demo_sign` is undefined | `unknown_runtime_error` | Verify bundle was loaded AFTER shim; check bundle syntax with `node --check` | A0 |
| Wrong shim surface | Shim loaded but provides wrong method signatures | `unknown_runtime_error` | Inspect shim exports; compare expected API surface with actual | A1 |
| Unknown runtime error | Error text does not match any known pattern | `unknown_runtime_error` | Check stderr manually; add new pattern to classifier if recurring | A2 |

## How the Classifier Works

The `runtime_error_classifier.py` performs case-insensitive pattern matching on stderr/stdout:

1. Check for `window is not defined` or `Cannot read properties of undefined ... window` → `missing_window`
2. Check for `document is not defined` → `missing_document`
3. Check for `navigator is not defined` → `missing_navigator`
4. Check for `EventTarget is not defined` → `missing_event_target`
5. Check for `localStorage is not defined` → `missing_local_storage`
6. If no pattern matches → `unknown_runtime_error`

## Safety

- All patterns are observed in synthetic/local Node.js subprocesses
- No real websites involved
- No real platform bypass methods described
- Classifier is rule-based (no ML model, no external API calls)
