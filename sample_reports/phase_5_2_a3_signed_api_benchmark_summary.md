# Phase 5.2-A3: Synthetic Signed API Benchmark Summary

**Date**: 2026-06-24
**Status**: PASS
**Source commit**: 4ed256e5 (D:\LearnSpider)

## Goal

A3 extends beyond single x-demo-signature to a full signed API benchmark with 6 dependency-matrix cases. All synthetic/local mock only.

## Case Results

| Case | Dep Count | Dependencies | Signed | Verified | Negative Rejected |
|------|:---:|-------------|:---:|:---:|:---:|
| path_payload_basic | 3 | method, path, payload | ✅ | ✅ | ✅ |
| timestamp_nonce | 5 | +timestamp, +nonce | ✅ | ✅ | ✅ |
| user_agent_salt | 5 | +userAgent, +localStorage salt | ✅ | ✅ | ✅ |
| document_meta_token | 4 | +document meta token | ✅ | ✅ | ✅ |
| event_token | 4 | +synthetic event token | ✅ | ✅ | ✅ |
| full_dependency_matrix | 9 | all 9 dependencies | ✅ | ✅ | ✅ |

## Key Metrics

| Metric | Value |
|--------|------:|
| total_cases | 6 |
| signed_cases | 6 |
| verified_cases | 6 |
| negative_cases | 6 |
| negative_rejected | 6 |
| dependency range | 3–9 |
| external_network | 0 |
| real_platform_logic | 0 |
| overall_status | PASS |

## Signature Algorithm

WARBDemoV2: SHA-256 over ordered pipe-separated seed string containing case name, method, path, stable JSON payload, and all relevant dependencies.

## Safety

Synthetic only. No real platform signatures (x-s, x-t, x-s-common). No network requests. No cookies or Authorization. Local mock API with x-demo-signature only.
