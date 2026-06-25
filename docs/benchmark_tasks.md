# Standard Benchmark Tasks

WebAgentRuntimeBench now ships a six-task standard suite. Every task is synthetic, local-only, and safe to run after cloning the repository.

| Task ID | Task | What It Tests | Primary Output |
|---|---|---|---|
| `static_extraction` | Static Product List Extraction | Local HTML/schema extraction when fields are visible without runtime repair. | Fixed expected output fixture |
| `dynamic_runtime_missing` | Dynamic Runtime Missing Diagnosis | Missing browser runtime classification and synthetic shim recovery. | A0 `run_summary.json`, trace, replay |
| `bundle_shim_repair` | Bundle Shim Repair Variants | Five missing-runtime bundle variants plus full-shim recovery. | A2 summary, variant results, dashboard |
| `signed_mock_api` | Signed Mock API Verification | Six local signed mock API cases, dependency tracing, and tamper rejection. | A3 summary, signed results, trace |
| `failure_diagnosis` | Failure Diagnosis CLI | Rule-based diagnosis from synthetic failure traces. | `diagnosis.json`, repair prompt |
| `safety_guard` | Synthetic Safety Guard | No real-platform targets, no credentials, no executable network patterns. | Safety scan console result |

Run all tasks:

```powershell
python tools\benchmark\run_benchmark.py --out-dir sample_run\benchmark --node node
```

The runner writes:

- `sample_run\benchmark\benchmark_report.json`
- `sample_run\benchmark\benchmark_report.md`
- per-task artifacts under `sample_run\benchmark\tasks\`

The suite is intended for reproducible benchmark and debugging work. It is not a production crawler and does not access real websites.
