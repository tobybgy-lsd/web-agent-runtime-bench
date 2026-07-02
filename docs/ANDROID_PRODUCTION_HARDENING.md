# Android APK Production Hardening

Agent Failure Doctor v5.2.0 adds a local-only Android APK production hardening layer for authorized app automation evidence.

It focuses on app profiles, page objects, locator registry validation, locator healing recommendations, UI tree diffs, dry-run workflow templates, mock device matrices, local task queues, sanitized replay packs, and stability scoring.

Safety boundaries:

- Local evidence only.
- Authorized target declaration required.
- Dry-run by default.
- Final submit is blocked by default.
- Locator healing is recommendation-only and requires manual approval.
- Absolute coordinate primary locators are blocked.
- Blocked: APK modification, root-required execution, hook-style runtime changes, external upload, telemetry, or real platform access.
