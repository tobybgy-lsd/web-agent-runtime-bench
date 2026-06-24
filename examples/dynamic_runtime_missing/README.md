# Dynamic Runtime Missing Example

**Type**: Runtime failure trace sample
**Synthetic Only**: Yes. Demonstrates diagnosis and repair of missing browser APIs.

## Files

- `runtime_failure_trace_sample.jsonl` — 3 trace entries: missing_window, missing_document, repaired
- `failure_replay_sample.md` — Human-readable replay of the failures

## Scenario

A synthetic JS bundle requires `window`, `document`, and `localStorage` to run. When executed in a headless Node.js environment:

1. **No shim** → `ReferenceError: window is not defined` → classifier: `missing_window`
2. **Window only** → `ReferenceError: document is not defined` → classifier: `missing_document`
3. **Full shim** → Bundle loads, `__warb_demo_sign()` works → classifier: N/A (success)

## Key Takeaway

Runtime failures are predictable and classifiable. The repair strategy is uniform: load `synthetic_browser_shim.js`.
