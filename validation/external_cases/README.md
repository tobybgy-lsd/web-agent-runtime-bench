# External Cases

This directory is reserved for accepted external failure case metadata.

Initial state is intentionally empty. Do not add author-generated fixtures here and do not count templates as external cases.

Accepted files should be named with stable case ids:

```text
EXT-2026-0001.json
EXT-2026-0002.json
```

Each JSON file must follow `schemas/external_failure_case.schema.json` and should point to a sanitized input pack through `input_pack_path` when the raw material can be kept in the repository.

Source types:

- `public_external_issue`: submitted through this repository's GitHub issues
- `external_public_reference`: sourced from a traceable external public issue or Q&A
- `public_inspired_sanitized`: reconstructed from public patterns and not counted as external-user validation

