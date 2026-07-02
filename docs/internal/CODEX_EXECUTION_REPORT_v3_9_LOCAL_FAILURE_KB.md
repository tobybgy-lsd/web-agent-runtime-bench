# Codex Execution Report: v3.9 Local Failure Knowledge Base

## Goal

Add a local-only failure knowledge base to Agent Failure Doctor.

## Starting Version

v3.8.0 CI/CD Integration Pack.

## Added CLI

`failure-doctor kb init/status/import-report/import-batch/import-ci/search/match/list/show/promote-fix/mark-regression/export/validate/rebuild-index`.

## Storage Design

Plain JSON/JSONL files under `.failure-doctor-kb`, with case folders, indexes,
fix summaries, exports, and audit logs.

## Case Schema

Each case stores a sanitized summary, evidence fingerprint, safety metadata,
repair order, fix status, optional verified fix, tags, and notes.

## Fingerprint And Similarity

Local deterministic fingerprints and token matching. No external embedding API.

## Verified Fixes

Promoted only from local verification reports. Suggestions only; no auto-apply.

## Import And Export Policy

Sanitized-only import/export. Unsafe reports are blocked. Exports omit raw
evidence and private materials.

## Integration

`diagnose --kb`, `ci diagnose --kb`, console read APIs, and agent-bootstrap KB
workflow files.

## Validation

`python -m tools.validation.run_local_failure_kb_validation` writes
`validation/local_failure_kb_validation.json`.

Final verification results are recorded during release closeout.
