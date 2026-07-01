# Agent Failure Doctor v3.2.7 - Canvas Fingerprint Evidence Patch

v3.2.7 is a patch release for the v3.2 Auto Collector line. It adds
public-safe diagnosis for sanitized Canvas fingerprint evidence while
preserving the project boundary: local-first diagnosis only, no fingerprint
alteration recipes, and no bypass guidance.

## What changed

- Added public-safe anti-bot risk subtypes:
  - `canvas_fingerprint_collision`
  - `browser_canvas_fingerprint_risk`
- Extended `browser_runtime_report.json` support for sanitized Canvas
  hash/session-count summaries.
- Added `docs/CANVAS_FINGERPRINT_BOUNDARY.md` to document what may be
  published and what must remain local/private.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==3.2.7
failure-doctor --help
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

PyPI: <https://pypi.org/project/agent-failure-doctor/>

For local development from source:

```powershell
python -m unittest discover -s tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
python -m tools.validation.run_p98_master_gate
```

## Safety

This release keeps Canvas fingerprint signals as evidence-only diagnostics. It
does not ship local challenge solvers, flags, rendering-hook details, Canvas
output alteration recipes, fingerprint spoofing, CAPTCHA bypass, anti-bot
evasion, or default active probes.

Expected safety result:

```text
forbidden outputs: 0
private solution leaks: 0
real platform access: 0
```

## Known limits

- `browser_runtime_report.json` Canvas evidence is user supplied. Agent Failure
  Doctor does not verify how it was collected.
- These subtypes identify risk boundaries and evidence needs; they do not
  generate operational fingerprint alteration or bypass steps.
- If evidence is weak or authorization is unclear, the safe next action is to
  stop automation or use an official, authorized path.
