# Agent Failure Doctor v3.2.5 - Behavioral and Client Hints Evidence Patch

v3.2.5 is a patch release for the v3.2 Auto Collector line. It adds
public-safe diagnosis for user-supplied browser runtime and input-timing
evidence while preserving the project boundary: local-first diagnosis only, no
default active probes, and no bypass guidance.

## What changed

- Added `browser_runtime_report.json` as a recognized offline evidence input.
- Added `input_timing_summary.json` as a recognized offline evidence input.
- Added public-safe anti-bot risk subtypes:
  - `client_hints_platform_mismatch`
  - `browser_header_consistency_risk`
  - `keystroke_telemetry_anomaly`
  - `zero_interval_input_detected`
  - `behavioral_input_risk`
- Added `docs/BEHAVIORAL_CLIENT_HINTS_BOUNDARY.md` to document what may be
  published and what must remain local/private.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==3.2.5
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

This release keeps behavioral and Client Hints signals as evidence-only
diagnostics. It does not ship browser stealth code, input mimicry recipes,
CAPTCHA bypass, anti-bot evasion, fingerprint spoofing, signature cracking, or
default active network probes.

Expected safety result:

```text
forbidden outputs: 0
private solution leaks: 0
real platform access: 0
```

## Known limits

- `browser_runtime_report.json` and `input_timing_summary.json` are
  user-supplied summaries. Agent Failure Doctor does not verify how they were
  collected.
- These subtypes identify risk boundaries and evidence needs; they do not
  generate operational bypass steps.
- If evidence is weak or authorization is unclear, the safe next action is to
  stop automation or use an official, authorized path.
