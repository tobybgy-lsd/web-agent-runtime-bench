# Agent Failure Doctor v5.8.0 - Real Company APK Pilot Program Pack

This release adds local-only Android/mobile workflow governance capabilities. It uses mock or synthetic public examples, keeps raw evidence local-only, and keeps final submit and business mutation blocked by default.

## What changed

- Added public-safe Android/mobile automation governance surfaces for the release line.
- Added validation evidence and release documentation without adding unsafe automation capability.

## Install

```powershell
python -m pip install agent-failure-doctor==5.8.0
failure-doctor --help
```

## Safety

- Authorized workflows only.
- Sanitized reports by default.
- No external upload or telemetry by default.
- APK modification, privileged execution requirements, and runtime instrumentation are blocked by default.
- Final submit and business mutation remain blocked unless an explicit review policy is present.


## Reproduce

``powershell
python -m tools.validation.run_p98_master_gate
python -m tools.validation.run_package_private_content_scan
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
``

## Known limits

- Public examples remain mock or synthetic.
- Raw device evidence stays local-only.
- Forbidden output count remains 0 in the validation gate.

