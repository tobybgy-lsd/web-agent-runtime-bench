# Architecture

## Agent Failure Doctor

Agent Failure Doctor is the current product layer of this repository. It diagnoses local sanitized failure evidence from AI browser automation, Playwright, crawler, RPA, and business automation runs.

Input evidence:

```text
trace/log/network/description/screenshot metadata
```

Primary flow:

```text
capture or collect evidence
  -> diagnose
  -> plan
  -> verify
  -> optional sanitize/share
```

Short form:

```text
diagnose -> plan -> verify
```

The diagnostic core is a local rule engine with evidence scoring. It favors explainable, testable, CI-verifiable classifications over opaque model judgments. Future optional reasoning assist should consume the structured evidence bundle and produce prompts, hypotheses, and questions, but it must not replace the rule engine as the source of truth.

Key packages:

- `failure_doctor`: multi-input CLI, user-facing reports, fix plans, verification, auto capture, sanitize/share.
- `trace_doctor`: Playwright trace-specific diagnosis.
- `tools.failure_artifacts`: artifact schema, classifier, reports, issue drafts, fix plan and verification helpers.
- `integrations`: Playwright collector, generic log pack adapter, browser-use style adapters.
- `tools.validation`: validation runners and dashboards.

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
