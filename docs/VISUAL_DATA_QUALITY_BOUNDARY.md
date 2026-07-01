# Visual and Data Quality Boundary

Agent Failure Doctor v3.2.9 adds public-safe diagnostics for local data quality
and visual browser automation failures.

## Public scope

- `SchemaValidator`, `DedupeChecker`, `BloomDedupeChecker`, `CheckpointManager`,
  `RetryPolicy`, `DeadLetterQueue`, `RunManifest`, source hashing, and
  field-quality reports for authorized automation outputs.
- Structured JSONL trace logging for local run, page, record, and field-quality
  evidence.
- `failure-doctor visual-diagnose <input> --out <report>` for local screenshot,
  DOM, OCR, and click-coordinate evidence.
- Optional VLM request-pack helpers with `provider="mock"` as the default.
- Public-safe diagnosis subtypes for audio/runtime fingerprint evidence,
  TCP/IP OS-fingerprint mismatch evidence, and AST dynamic-token evidence.

## Out of scope

This public package must not include:

- local challenge solvers, flags, mock challenge servers, or private training
  answers;
- access-control circumvention, automated challenge solving, browser identity
  alteration, protocol impersonation, or behavioral imitation instructions;
- credential, cookie, token, or browser-profile extraction;
- real-platform collection logic or unauthorized automation guidance.

## Safe next action

Reports should point users toward sanitized evidence collection, data-integrity
checks, official APIs or SDKs, platform-approved exports, and stopping the run
when authorization is unclear.
