# Agent Failure Doctor v5.3.0 - Android Real Device Farm & Business Workflow Operations Pack

v5.3.0 adds a local-only Android Ops layer for authorized Android automation
operations.

## What changed

## Highlights

- `failure-doctor android-ops` command group.
- Mock-first Android device farm initialization, inventory, health, lease, and recovery.
- Local Appium session planning without starting real remote servers.
- Dry-run business workflow templates and data binding.
- Scheduler, replay, flaky detection, compatibility reporting, mutation guard, metrics, and runbook generation.
- Android Ops validation with 320 public-safe synthetic/mock cases.
- P98 pillars for Android real device farm, business workflow ops, and flaky flow detection.

## Safety

No abuse circumvention, device identity manipulation, APK tampering, runtime
instrumentation, privilege escalation, pooling-based evasion, raw screenshot upload,
or production state mutation is introduced. Final submit and production state
mutation are blocked by default.

Forbidden output count remains 0 across the v5.3.0 validation gate.

## Known limits

- Device and Appium operations are mock-first and local-only by default.
- Real business submissions remain blocked without explicit approval artifacts.
- This release does not change the stable API, schema, or plugin ABI contract.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==5.3.0
failure-doctor android-ops --help
python -m tools.validation.run_android_ops_validation
python -m tools.validation.run_p98_master_gate
```
