# Phase 5.1 Evaluation Harness Freeze

## Status: Frozen

The Phase 5.1-A3 evaluation harness has been frozen. This is NOT an Agent solving success.

## Key Results

| Metric | Value |
|--------|-------|
| Baseline challenges | 315/315 PASS (solvers) |
| Oracle guard | PASS (no leakage) |
| API key leak | 0 |
| Forbidden access | 0 |
| Agent solving PASS | 0 |
| Exact preimage reconstruction | OPEN BOTTLENECK |

## What Was Frozen

- 315 baseline challenges with public canonical web scraping patterns
- Full evaluation harness (collector, classifier, router, evaluator, oracle guard)
- 30-case aggregate retry pipeline
- Response shape router (wrong_flat_overroute = 0/30)
- Candidate generation pipeline (flat, nested, config-aware)

## Open Bottleneck

The **exact preimage reconstruction** problem remains unsolved. Agent generates near-correct raw_preimage candidates but fails exact match against expected_answer due to separator, order, salt/nonce, and visibility filter mismatches. This is a known limitation, not a claim of solution.
