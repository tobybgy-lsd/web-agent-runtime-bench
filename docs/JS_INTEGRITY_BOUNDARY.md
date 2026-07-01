# JavaScript Integrity Evidence Boundary

Agent Failure Doctor v3.2.6 can ingest sanitized, user-supplied evidence about
JavaScript request-integrity failures. This is a diagnostic boundary, not a
deobfuscation, signature reconstruction, or anti-bot evasion feature.

## Supported offline input

Place this file in a failed-run directory before running `failure-doctor
diagnose`:

```text
js_integrity_report.json
```

The file is treated as a sanitized evidence summary. Agent Failure Doctor does
not fetch JavaScript bundles, execute browser scripts, run AST recovery, or
derive request signatures.

## Public-safe diagnoses

The public package may classify these subtypes:

```text
obfuscated_js_integrity_required
js_ast_obfuscation_detected
rotated_string_array_detected
client_generated_token_missing
request_integrity_algorithm_changed
```

The recommended output is intentionally limited to:

- treating the issue as a JavaScript/request-integrity boundary
- collecting sanitized JS bundle metadata, function-name summaries,
  request-parameter diffs, and HTTP rejection evidence
- checking for an authorized API, official SDK, documented export, or
  platform-approved test hook
- stopping automation when authorization or platform terms are unclear

## Not included

The public project must not include:

- private challenge solvers
- challenge flags or private target details
- AST recovery or deobfuscation recipes
- string-array offsets, formulas, constants, or computed token values
- signature reconstruction code
- anti-bot evasion or access-control defeat steps
- default active JavaScript, browser, TLS, IP, or network probes

Keep private training assets local. Only publish generalized, sanitized
diagnostic patterns and safety-preserving tests.
