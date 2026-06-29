# Auto Collector

Agent Failure Doctor v3.2.0 adds an authorized local collector for failed automation projects.

```powershell
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize
```

## What It Collects

- Playwright traces, reports, screenshots, videos, console logs, and config hints.
- Selenium, Puppeteer, Cypress, Scrapy, requests/httpx, generic RPA, and generic log evidence.
- Text logs, network summaries, screenshot metadata, local run summaries, and user descriptions.

## What It Writes

```text
failure_doctor_auto_report/
|-- collection_manifest.json
|-- collection_summary.md
|-- open_this_first.md
|-- raw_local_only_do_not_share/
|-- sanitized_failure_pack/
|-- report/
|-- fix_plan/
`-- ai_handoff/
```

## Safety Model

The collector is local-only, project-scoped, and copy-only. It skips dependency folders, Git internals, virtualenvs, browser profiles, credential stores, and SSH keys. It does not upload artifacts.

Use `--dry-run` to inspect the manifest without copying raw files.
