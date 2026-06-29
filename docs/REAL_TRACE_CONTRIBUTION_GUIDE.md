# Real Trace Contribution Guide

This project accepts only sanitized, local-first failure evidence.

## What Helps

- A sanitized Playwright `trace.zip`
- `error.log` or `console.txt`
- `network.json` with secrets removed
- `user_description.txt` explaining what the automation expected and what happened
- Screenshot metadata or redacted screenshots when allowed

## Before Sharing

Remove:

- passwords
- API keys
- cookies
- tokens
- authorization headers
- private URLs
- personal data
- customer data

If you are not sure whether a trace contains private data, do not upload it publicly. Open an issue with a short sanitized excerpt first.

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

## Public Test Case Checklist

- The failure can be described without exposing secrets.
- The source URL is public, or the case is marked as sanitized/public-inspired.
- The expected diagnosis is written down.
- The minimal reproduction uses a local or mock site when possible.
- The report does not request challenge solving, access-control circumvention, credential extraction, or unauthorized collection.
