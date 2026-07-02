# Benchmark Runner

Run:

```powershell
failure-doctor benchmark run --suite public-safe --out .\benchmark_report
failure-doctor benchmark run --suite regression --out .\benchmark_report
failure-doctor benchmark compare --baseline .\old_report --candidate .\new_report --out .\benchmark_diff
failure-doctor benchmark validate-suite --suite examples\public_benchmark_cases
```

Outputs include `benchmark_manifest.json`, `benchmark_summary.md/json`,
`case_results.jsonl`, `failures.md`, `regression_diff.json`, and
`open_this_first_benchmark.md`.
