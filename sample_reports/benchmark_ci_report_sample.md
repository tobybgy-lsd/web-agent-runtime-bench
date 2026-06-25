# WebAgentRuntimeBench Benchmark Report

- Benchmark version: `2026-06-25`
- Suite: `standard_synthetic_public_safe`
- Overall status: **PASS**
- Overall score: **100.0**
- Safety: synthetic-only, local-only, no credentials, no real-platform targets

## Reproduce

```powershell
python tools\benchmark\run_benchmark.py --out-dir sample_run\benchmark --node node
```

## Scores

| Task | Status | Score | Baseline | Scenario |
|---|:---:|---:|---|---|
| Static Product List Extraction | PASS | 100.0 | naive_static_parser | Product detail or listing pages where fields are visible in HTML. |
| Dynamic Runtime Missing Diagnosis | PASS | 100.0 | no_shim_vs_full_shim | Debugging Agent failures on JavaScript-rendered pages. |
| Bundle Shim Repair Variants | PASS | 100.0 | partial_runtime_vs_full_runtime | Choosing which browser APIs a headless Agent runtime must provide. |
| Signed Mock API Verification | PASS | 100.0 | positive_only_vs_negative_guarded | Understanding local API dependency tracing for request verification without real signatures. |
| Failure Diagnosis CLI | PASS | 100.0 | manual_trace_inspection | Turning Agent failure traces into actionable repair instructions. |
| Synthetic Safety Guard | PASS | 100.0 | no_safety_gate_vs_local_safety_gate | Public benchmark release review and artifact hygiene. |

## Safety Boundary

- External network: forbidden
- Real platform signatures/endpoints: forbidden
- Cookies or Authorization headers: forbidden
- All tasks use local synthetic fixtures or mock APIs
