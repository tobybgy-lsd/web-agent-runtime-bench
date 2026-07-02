# Agent Failure Doctor v5.1.0 - Android APK UI Automation Adapter Pack

v5.1.0 adds a public-safe, local-only Android APK UI automation adapter.

## Install

```powershell
python -m pip install agent-failure-doctor==5.1.0
failure-doctor --help
```

## What changed

- New `failure-doctor android ...` command group.
- New `diagnose --adapter android-apk` and `collect --adapter android-apk`.
- Android UI tree, flow, locator, diagnosis, run, replay, safety, device, step,
  and media schemas.
- Public-safe Android APK example cases.
- Android APK automation validation with 220 synthetic local cases.
- New P98 pillars:
  - `android_apk_ui_automation`
  - `android_ui_tree_diagnostics`
  - `mobile_flow_replay`

## Reproduce

```powershell
python -m tools.validation.run_android_apk_automation_validation
python -m tools.validation.run_p98_master_gate
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

## Safety

The adapter is local-only and evidence-bound. It supports authorized/mock app
diagnosis, dry-run flow validation, UI tree inspection, and logcat evidence
summaries. It does not add any private training solution, platform access, APK
modification, external upload, or unsupported anti-abuse guidance. Final submit
steps remain blocked by default. Forbidden output count remains 0.

## Compatibility

No breaking changes are made to the v5.0 Stable API / Schema / Plugin ABI
baseline. v5.1 extends the CLI and schema registry with Android APK evidence
schemas.

## Known limits

- Real-device execution depends on locally installed and authorized Android
  tooling.
- The public validation suite uses local synthetic fixtures and mock evidence.
- Ecosystem maturity remains outside the controlled P98 score.
