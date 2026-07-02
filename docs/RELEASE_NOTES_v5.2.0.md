# Agent Failure Doctor v5.2.0 - Android APK Production Hardening & Workflow Template Pack

v5.2.0 extends the Android APK UI adapter with production hardening surfaces for authorized local workflows.

## What changed

- `failure-doctor android-pro` command group.
- Android app profile init/validate/inspect.
- Page object generation from UIAutomator XML.
- Locator registry build/validate.
- Recommendation-only locator healing.
- UI tree diff.
- Safe Android workflow template library.
- Mock device matrix runner.
- Local task queue and sanitized failure replay pack.
- Android stability score and onboarding check.
- P98 pillars for Android production hardening, locator self-healing, and device matrix runner.

## Safety

- No new API, schema, or plugin ABI breaking changes.
- Blocked by design: external upload, telemetry, APK modification, hook-style runtime changes, root-required execution, or real platform access.
- Final submit remains blocked by default.
- Absolute coordinate primary locators are blocked.

Forbidden output count remains 0 across the v5.2.0 validation gate.

## Known limits

- Android Pro workflows are local evidence, mock matrix, and dry-run focused.
- Locator healing is a recommendation surface only and requires manual review.
- Real device operation remains outside the default public validation path.

## Reproduce

```powershell
python -m pip install agent-failure-doctor==5.2.0
failure-doctor android-pro --help
python -m tools.validation.run_android_production_hardening_validation
python -m tools.validation.run_p98_master_gate
```
