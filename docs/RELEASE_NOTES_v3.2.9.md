# Agent Failure Doctor v3.2.9 - Visual and Data Quality Diagnostics Patch

v3.2.9 is a patch release for the v3.2 Auto Collector line. It promotes local
data-quality and visual-failure helpers into the public package while keeping
private training solvers and challenge details out of GitHub and PyPI.

## What changed

- Added reusable data engineering stability helpers:
  - schema validation
  - set-based and Bloom-filter deduplication
  - checkpoints
  - retry bookkeeping
  - dead-letter queues
  - run manifests
  - source hashes
  - field-quality reports
  - structured JSONL trace logging
- Added `failure-doctor visual-diagnose <input> --out <report>` for sanitized
  screenshot, DOM, OCR, and click-coordinate evidence.
- Added optional local-first VLM visual analyzer helpers. Mock mode is the
  default, and no network call is made unless a caller explicitly selects a
  provider and has configured that provider locally.
- Added precise public-safe subtypes:
  - `audio_fingerprint_risk`
  - `tcp_ip_os_fingerprint_mismatch`
  - `ast_dynamic_token_required`
- Added `docs/VISUAL_DATA_QUALITY_BOUNDARY.md`.

## Safety

- Forbidden outputs remain at 0 in the local safety scan.
- The package remains diagnosis-only.
- No local challenge solvers, flags, mock challenge servers, browser stealth
  recipes, fingerprint spoofing instructions, behavioral mimicry steps, or
  private solution details are included.
- Visual and data-quality outputs ask for sanitized evidence and authorized
  workflows rather than access-control defeat.

## Known limits

- Visual diagnosis is heuristic unless users provide richer evidence such as a
  trace or a real screenshot.
- The VLM helper only packages prompts and can run in mock mode locally; it is
  not a hosted vision service.
- Bloom-filter dedupe can have false positives by design.
- Data-quality helpers validate outputs; they do not repair business logic by
  themselves.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==3.2.9
failure-doctor --help
failure-doctor visual-diagnose .\examples\failed_runs\visual_overlay --out .\visual_report
```

PyPI: <https://pypi.org/project/agent-failure-doctor/>

From source:

```powershell
python -m unittest discover -s tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
python -m tools.validation.run_p98_master_gate
```
