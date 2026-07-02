# Public Benchmark Spec

Each public case contains:

- `case_manifest.json`
- `input/`
- `expected/`
- `README.md`
- `LICENSE.md`
- `SAFETY.md`

Required manifest booleans:

- `public_safe: true`
- `sanitized: true`
- `diagnosis_only_no_bypass: true`
- all real secret, customer data, PII, PHI, credentials, and private solution
  flags set to false
