# Android Ops Documentation Index

Agent Failure Doctor v5.3.0 adds a local-only Android real device farm and business workflow operations layer.

Start here:

- `docs/ANDROID_REAL_DEVICE_FARM.md`
- `docs/ANDROID_APPIUM_ORCHESTRATION.md`
- `docs/ANDROID_DEVICE_LEASE_AND_RECOVERY.md`
- `docs/ANDROID_BUSINESS_WORKFLOW_TEMPLATES.md`
- `docs/ANDROID_BUSINESS_DATA_BINDING.md`
- `docs/ANDROID_WORKFLOW_SCHEDULER.md`
- `docs/ANDROID_FLAKY_FLOW_DETECTION.md`
- `docs/ANDROID_COMPATIBILITY_REPORT.md`
- `docs/ANDROID_REAL_DEVICE_REPLAY.md`
- `docs/ANDROID_MUTATION_GUARD.md`
- `docs/ANDROID_OPS_DASHBOARD.md`
- `docs/ANDROID_PRODUCTION_RUNBOOK.md`

Safety boundary:

- Local-only device and artifact handling.
- Dry-run by default.
- Final submit and business mutation are blocked unless an explicit approval artifact is provided.
- No external screenshot upload, credential-store access, browser-profile access, APK modification, root requirement, or runtime instrumentation.

