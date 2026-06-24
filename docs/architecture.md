# Architecture

## Phase 5.1: AI-Agent Web Extraction Evaluation Harness

- 315 baseline challenges (public canonical web scraping patterns)
- Visible observation pipeline: pre-collected page/API data to compact observation to agent input
- Preimage candidate generator: multi-rule raw_preimage extraction from API responses
- Response shape router: classifies API responses (flat/nested/config/mixed JSON)
- Evaluation harness: evaluator, oracle guard, failure replay, capability dashboard

Key design: Agent never sees hidden_oracle, expected_answer, /api/check-answer, or /admin. Only visible observations.

## Phase 5.2: Synthetic Dynamic Web Runtime Benchmark

- Runtime error classifier: rule-based pattern matching for missing browser APIs
- Synthetic browser shim: IIFE providing EventTarget, localStorage, navigator, document, window stubs
- Synthetic bundles: runtime contract check bundles requiring specific browser globals
- Mock signed API: local SHA-256 signature verification (x-demo-signature, WARBDemoV1)
- Dependency tracer: tracks sign_function inputs (path, payload_hash, UA, salt, algorithm)

## Runner Flow

1. Node.js subprocess runs synthetic JS entry
2. Bundle checks runtime globals (throws ReferenceError if missing)
3. Classifier identifies error_type (missing_window, missing_document, etc.)
4. Repair: load shim.js before bundle
5. Full shim success: bundle exports window.__warb_demo_sign
6. Mock API: verify x-demo-signature locally
7. Trace to failure_replay.md and capability_dashboard.md

## Safety

All Phase 5.2 code is synthetic-only. No external network, no real signatures, no real platforms.
