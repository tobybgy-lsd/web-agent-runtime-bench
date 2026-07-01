# Agent Failure Doctor v3.4.0 - Visual Agent Runtime Observability Pack

v3.4.0 adds a local-only visual runtime observability layer for screenshot-driven
AI browser agents, RPA flows, and Computer Use style runs.

## Install

```powershell
python -m pip install agent-failure-doctor==3.4.0
failure-doctor --help
```

PyPI: https://pypi.org/project/agent-failure-doctor/

## New commands

```powershell
failure-doctor visual-runtime diagnose --input .\visual_run --out .\visual_report --no-dom
failure-doctor visual-runtime profile --input .\visual_run --out .\visual_profile
failure-doctor visual-runtime compare --baseline .\run_a --candidate .\run_b --out .\compare_report
failure-doctor visual-runtime adapt --source generic --input .\artifact_dir --out .\visual_run
failure-doctor visual-runtime validate --input .\visual_run --out .\validation_report
```

## What changed

- Added offline visual-run artifact loading and validation.
- Added visual runtime profile, screenshot cost, action grounding, coordinate
  drift, stale observation, context loss, and comparison reports.
- Added deterministic mock VLM support with external calls disabled by default.
- Added agent-bootstrap workflow guidance for visual-agent failures.

## Validation

- Adds `visual_agent_runtime_observability` to the P98 master gate.
- Adds at least 140 local-only synthetic visual runtime cases.
- Requires zero external VLM calls, zero screenshot uploads, zero real-platform
  access, zero forbidden output, and zero private solution leaks.

## Safety

The visual runtime pack diagnoses offline artifacts only. It does not provide
CAPTCHA bypass, anti-bot evasion, fingerprint spoofing, signature cracking,
protected-site challenge automation, or behavior imitation recipes.

Forbidden output count is required to stay zero.

## Reproduce

```powershell
python -m tools.validation.run_visual_agent_runtime_validation
python -m tools.validation.run_p98_master_gate
scripts\local_safety_scan.ps1
```

## Known limits

- v3.4 does not include a real VLM model.
- v3.4 does not upload screenshots or call cloud providers by default.
- v3.4 does not infer hidden DOM structure from screenshots.
- v3.4 diagnoses visual runtime evidence; it does not guarantee an automatic
  source-code patch for every visual-agent failure.
