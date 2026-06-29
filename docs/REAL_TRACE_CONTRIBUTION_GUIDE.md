# Real Trace Contribution Guide

You do not need to write code to contribute.

The most useful contribution is a sanitized failure case:

- `trace.zip`
- `error.log`
- `console.txt`
- `network.json`
- screenshot metadata
- `user_description.txt`

## Remove Before Sharing

- credentials
- cookies
- tokens
- authorization headers
- API keys
- private data
- private URLs
- customer data
- personal information

If you are not sure whether a file is safe to share, submit only a short sanitized excerpt and describe what happened.

## Recommended Folder Shape

```text
my_failed_run/
|-- trace.zip
|-- error.log
|-- console.txt
|-- network.json
|-- user_description.txt
`-- source.md
```

Run locally:

```powershell
failure-doctor diagnose .\my_failed_run --out .\report
```

## How A Case Is Accepted

1. Open an external failure case issue.
2. Confirm the material contains no credentials, cookies, tokens, or private data.
3. Maintainers assign a stable id such as `EXT-2026-0001`.
4. The current released version is run before diagnosis rules are changed.
5. The result is recorded in `validation/external_validation_dashboard.md`.
6. If the case exposes a gap, a future fix may add a regression test.

Templates and local synthetic examples are not counted as external cases.

## Public Test Case Checklist

- The failure can be described without exposing secrets.
- The source URL is public, or the case is marked as sanitized/public-inspired.
- The expected diagnosis is written down.
- The minimal reproduction uses a local or mock site when possible.
- The report does not request challenge solving, access-control circumvention, credential extraction, or unauthorized collection.
