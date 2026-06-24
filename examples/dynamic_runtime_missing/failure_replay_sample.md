# Runtime Failure Replay (Sample)

## Failure #1: missing_window

- **Input**: Node.js subprocess, no shim, bundle requires `window`
- **Error**: `ReferenceError: window is not defined`
- **Classifier**: `missing_window` (confidence 0.93)
- **Repair**: Load `synthetic_browser_shim.js` before bundle
- **Result**: ✅ Bundle loads

## Failure #2: missing_document

- **Input**: Node.js subprocess, `window` defined, no `document`
- **Error**: `ReferenceError: document is not defined`
- **Classifier**: `missing_document` (confidence 0.93)
- **Repair**: Add document stub (querySelector, createElement)
- **Result**: ✅ Bundle loads

## Full Shim Success

- **Input**: Full shim loaded → all browser globals stubbed
- **Result**: `window.__warb_demo_sign()` functional, mock API verification passes
- **Dependencies traced**: path, payload_hash, user_agent, local_salt, algorithm

---

*All cases are synthetic/local only. No real platforms.*
