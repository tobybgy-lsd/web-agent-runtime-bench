# Local Failure KB Examples

This folder is reserved for public-safe KB examples.

Use the CLI to generate local examples:

```powershell
failure-doctor kb init --path .\.failure-doctor-kb
failure-doctor kb import-report --kb .\.failure-doctor-kb --report .\report
failure-doctor kb match --kb .\.failure-doctor-kb --report .\report --out .\kb_match_report
```

Do not place raw logs, screenshots, traces, secrets, private local training materials, flags, or
challenge artifacts in this folder.
