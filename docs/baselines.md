# Comparison Baselines

The benchmark includes baseline families so results are interpretable rather than just pass/fail.

| Baseline | Purpose |
|---|---|
| `naive_static_parser` | Shows what local static extraction can solve before dynamic runtime handling is needed. |
| `no_shim_vs_full_shim` | Compares direct Node execution failures against synthetic browser shim recovery. |
| `partial_runtime_vs_full_runtime` | Shows which browser runtime surfaces are required for bundle compatibility. |
| `positive_only_vs_negative_guarded` | Separates happy-path signed mock API success from robust tamper rejection. |
| `manual_trace_inspection` | Contrasts raw trace review with rule-based diagnosis artifacts. |
| `no_safety_gate_vs_local_safety_gate` | Makes release hygiene measurable instead of implicit. |

These are local synthetic baselines. They are not comparisons against real websites, real signatures, or anti-bot systems.

## How to Read Results

- A static parser pass means the fixture is straightforward; it does not prove dynamic-page capability.
- A no-shim failure followed by full-shim success shows the runtime contract is understood.
- Positive signed mock API verification is not enough; negative rejection is required to avoid fake pass bugs.
- Safety pass means the artifact is acceptable for public benchmark demonstration, not for real-platform scraping.
