# Signed API Dependency Patterns

All cases are from Phase 5.2-A3 synthetic signed API benchmark. The signature header `x-demo-signature` and algorithm `WARBDemoV2` are **synthetic/local mock only**. Not real-platform signature implementations.

## Case Reference

| Case | Dependencies | Positive Verification | Negative Rejection | Lesson |
|------|-------------|:---:|:---:|--------|
| path_payload_basic | method, path, payload (3) | ✅ | ✅ | Minimum viable signed API: path + payload are sufficient for basic integrity check |
| timestamp_nonce | +timestamp, +nonce (5) | ✅ | ✅ | Adding timestamp prevents replay attacks; nonce ensures uniqueness |
| user_agent_salt | +userAgent, +localStorage salt (5) | ✅ | ✅ | Client environment fingerprint can be part of signature without storing server-side state |
| document_meta_token | +document meta token (4) | ✅ | ✅ | DOM-level tokens can bind a request to a specific page context |
| event_token | +synthetic event token (4) | ✅ | ✅ | Event-driven tokens enable request chaining verification |
| full_dependency_matrix | all 9 dependencies | ✅ | ✅ | Maximum dependency coverage; tampering any single input invalidates signature |

## Algorithm

```
WARBDemoV2|<caseName>|<method>|<path>|<stableJson(payload)>|
<timestamp>|<nonce>|<userAgent>|<salt>|<documentMetaToken>|<eventToken>
```

Hash with SHA-256, prefix with `demo_`.

## Negative Verification

Each case is tested with a **tampered payload** (adds `{"tampered": true}`). The verification system must reject all 6 tampered requests. Without negative tests, a system that always returns `accepted: true` would pass — a "fake pass" bug.

## Safety

- `x-demo-signature` only — no x-s, x-t, x-s-common
- WARBDemoV2 is a synthetic SHA-256 mock, not a real signing algorithm
- No Cookie or Authorization headers
- No external network requests
- No real platform logic
