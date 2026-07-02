# Agent Failure Doctor v3.7 Local Web Console

The local web console is a browser-based viewer for existing Agent Failure
Doctor reports. It is designed for people who want a readable cockpit for
diagnosis, evidence, safety, handoff, patch proposal previews, visual runtime,
OCR/document, regulated workflow, batch/fleet, and full-chain evaluation output
without uploading artifacts anywhere.

## Start

```powershell
failure-doctor console
failure-doctor console --host 127.0.0.1 --port 8765
failure-doctor console --workspace .\.failure-doctor-console
failure-doctor console --import-report .\report --open
```

Defaults:

- Host: `127.0.0.1`
- Port: `8765`
- Workspace: `.failure-doctor-console`
- Browser: not opened unless `--open` is passed
- Telemetry: disabled
- External assets: disabled

Binding to `0.0.0.0` or another non-loopback host is blocked unless
`--allow-lan` is explicitly provided.

## Views

- Dashboard
- Report Viewer
- Evidence Chain
- Safety Center
- AI Handoff Center
- Patch Proposal Center
- Visual Runtime Viewer
- OCR/Document Evidence Viewer
- Regulated Workflow Viewer
- Batch/Fleet Viewer
- Full-chain Evaluation Viewer
- History/Search
- Settings/Safety Policy

Missing report sections are shown as unavailable rather than failing the whole
page.

## Safety Boundary

The console is local-first and report-oriented:

- It does not upload screenshots, traces, logs, documents, or reports.
- It does not load CDN scripts or remote CSS.
- It does not send telemetry.
- POST actions require the local console token printed at startup.
- Raw local evidence is hidden by default.
- Shareable output should come from `failure-doctor sanitize` or a sanitized
  share pack.
- Patch proposal views are read-only previews. The console does not apply code
  changes.

The console must not be used to expose browser profiles, credential stores,
private keys, cookies, local-only raw evidence, or private training solutions.
