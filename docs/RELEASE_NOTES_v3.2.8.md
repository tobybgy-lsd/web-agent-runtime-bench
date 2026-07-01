# Agent Failure Doctor v3.2.8 - Deep Runtime Evidence Patch

v3.2.8 is a patch release for the v3.2 Auto Collector line. It adds
public-safe diagnosis for sanitized deep runtime, protocol-stack, client-VM,
and behavioral evidence while preserving the project boundary: local-first
diagnosis only, no bypass guidance, and no private challenge solution leaks.

## What changed

- Added public-safe browser runtime evidence subtypes:
  - `webgl_virtual_renderer_detected`
  - `webrtc_private_ip_leak_detected`
  - `automation_global_scope_leak_detected`
  - `runtime_sandbox_leak_detected`
  - `native_function_integrity_mismatch`
  - `debugger_timing_anomaly`
- Added public-safe protocol and client-VM evidence subtypes:
  - `http2_settings_fingerprint_mismatch`
  - `ja4_h2_fingerprint_mismatch`
  - `js_vmp_integrity_check_failed`
  - `numeric_semantics_mismatch`
- Added public-safe behavioral telemetry evidence subtypes:
  - `pointer_trajectory_entropy_anomaly`
  - `mathematical_trajectory_detected`
- Extended offline report support for `browser_runtime_report.json`,
  `probe_report.json`, `js_integrity_report.json`, and
  `input_timing_summary.json`.
- Added `docs/DEEP_RUNTIME_PROTOCOL_BEHAVIOR_BOUNDARY.md` to document what may
  be published and what must remain local/private.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==3.2.8
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

This release keeps deep runtime, protocol, client-VM, and behavioral telemetry
signals as evidence-only diagnostics. It does not ship local challenge solvers,
flags, browser runtime alteration recipes, protocol impersonation values, VMP
reconstruction logic, behavioral mimicry steps, CAPTCHA bypass, anti-bot
evasion, or default active probes.

Expected safety result:

```text
forbidden outputs: 0
private solution leaks: 0
real platform access: 0
```

## Known limits

- Offline evidence reports are user supplied. Agent Failure Doctor does not
  verify how the summaries were collected.
- These subtypes identify risk boundaries and evidence needs; they do not
  generate operational runtime alteration, transport alignment, or bypass steps.
- If evidence is weak or authorization is unclear, the safe next action is to
  stop automation or use an official, authorized path.
