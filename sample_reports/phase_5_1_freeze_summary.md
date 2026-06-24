# Phase 5.1 Evaluation Harness Freeze Summary

**Date**: 2026-06-24
**Status**: FROZEN
**Tag**: phase5-1a-a3-evaluation-harness-freeze-v1

## Baseline

| Metric | Value |
|--------|-------|
| Baseline challenges | 315 |
| Baseline pass rate | 315/315 (100%) |
| Solver registry | 61 solvers |
| Challenge depth audit | Average 8.22/10 |

## Agent Evaluation (30-case)

| Metric | Value |
|--------|------:|
| Agent attempts | 30 |
| Non-empty answers | 25/30 |
| Candidate valid | 30/30 |
| PASS | 0 |
| FAIL | 30 |

## Architecture

- **Visible observation pipeline**: Agent only sees pre-collected page/API data — never accesses hidden oracle, expected answer, /api/check-answer, or /admin.
- **Preimage candidate generator**: Multi-rule raw_preimage extraction from API responses.
- **Response shape router**: Classifies API responses as flat/nested/config/mixed JSON.
- **Evaluation harness**: Evaluator + oracle guard + failure replay + capability dashboard.

## Key Finding

**Exact preimage reconstruction is the bottleneck.** The agent can select valid candidates but cannot reliably reconstruct the exact raw preimage (separator ordering, salt/nonce combinations, visible/decoy filtering). This is an open research problem, not a solved claim.

## Status

The evaluation harness is frozen. Agent solving is not claimed as solved. This is a benchmark framework, not a production crawler.
