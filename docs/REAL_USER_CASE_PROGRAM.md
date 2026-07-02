# Real User Case Program

Agent Failure Doctor v4.3 adds a local-first intake path for turning failure
materials into sanitized, public-safe cases.

Commands:

```powershell
failure-doctor case intake --input .\raw_failure_pack --out .\sanitized_case
failure-doctor case anonymize --input .\raw_failure_pack --out .\anonymous_case
failure-doctor case validate --case .\anonymous_case
failure-doctor case publish-check --case .\anonymous_case
failure-doctor case export-public --case .\anonymous_case --out .\public_case
```

The program is local-only by default. It does not upload traces, screenshots,
logs, OCR output, PDFs, knowledge-base content, or CI artifacts.
