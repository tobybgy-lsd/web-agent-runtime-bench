# Agent Failure Doctor v3.2.0 - Auto Collector & One-Click Diagnosis Pack

v3.2.0 adds authorized local evidence collection and one-click diagnosis on top of the v3.1 P98 diagnostic core.

## What changed

- Added `failure-doctor collect --project <dir> --preset auto --out <report> --auto-diagnose --auto-handoff --auto-sanitize`.
- Added `failure-doctor watch --project <dir> --out <reports> --once --auto-diagnose`.
- Added `failure-doctor run --capture -- <command>` compatibility.
- Added project-scoped `collection_manifest.json`, `collection_summary.md`, `open_this_first.md`, raw-local-only evidence storage, sanitized packs, diagnosis reports, fix plans, and AI handoff packs.
- Added Windows one-click launchers under `scripts/windows/`.
- Added `tools.validation.run_auto_collector_validation` and promoted Auto Collector to the P98 master gate.

## Reproduce

```powershell
python -m pip install -e .
python -m tools.validation.run_auto_collector_validation
python -m tools.validation.run_p98_master_gate
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize
```

## Safety

- Local-first and no upload.
- No whole-computer scan.
- No browser profile or credential-store access.
- No `.git`, dependency folder, virtualenv, SSH key, or cookie-store collection.
- Sanitized sharing remains manual-review-first.
- Forbidden outputs remain 0.

## Known limits

- Screenshot handling is metadata-first; image understanding is not part of v3.2.0.
- Watch mode uses polling and is intentionally conservative.
- The collector does not repair source code automatically; it prepares diagnosis, fix plan, and AI handoff artifacts.
- Ecosystem maturity, stars, PyPI downloads, and third-party integrations remain outside the controlled maturity score.
