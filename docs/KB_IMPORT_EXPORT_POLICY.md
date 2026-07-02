# KB Import And Export Policy

Import accepts sanitized Failure Doctor reports and CI summaries.

Blocked by default:

- raw local-only artifacts
- raw logs, screenshots, traces, OCR text, PDFs, or customer data
- secrets, cookies, authorization headers, API keys, passwords, tokens
- private local training materials, flags, challenge artifacts, or private lab notes
- unsafe recommendations or access-control defeat guidance

Export is sanitized-only:

```powershell
failure-doctor kb export --kb .\.failure-doctor-kb --out .\kb_export --sanitized-only
```

The export contains case summaries, evidence fingerprints, verified fix
summaries, regression tags, and aggregate stats.
