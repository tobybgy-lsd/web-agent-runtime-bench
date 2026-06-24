# Signed API Dependency Matrix Example

**Type**: Signed API dependency trace sample
**Synthetic Only**: Yes. Uses WARBDemoV2 algorithm, x-demo-signature header.

## Files

- `dependency_matrix_sample.json` — 6 cases with dependency counts and verification status
- `signed_api_trace_sample.jsonl` — Sample trace showing case_signed, dependencies_traced, mock_api_verified steps

## Cases

All 6 cases pass positive verification and negative (tampered-payload) rejection. Dependency count ranges from 3 to 9.

No real platforms. No x-s/x-t/x-s-common. No Cookie/Authorization. No external network.
