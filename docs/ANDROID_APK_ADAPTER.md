# Android APK UI Automation Adapter

Agent Failure Doctor v5.1 adds a local-only Android APK UI automation evidence
adapter for authorized, owned, internal, or mock app workflows.

## What It Accepts

- Appium-style logs
- ADB/uiautomator XML dumps
- logcat excerpts
- screenshot metadata or local screenshots
- Android UI flow files
- local run/replay reports

## Commands

```powershell
failure-doctor android doctor --out .\android_doctor
failure-doctor android devices --out .\android_devices
failure-doctor android dump-ui .\examples\android_apk_cases\ui_tree_basic\input\ui.xml --out .\android_ui
failure-doctor android validate-flow .\examples\android_apk_cases\post_image_text_dry_run\input\flow.yml --out .\android_flow
failure-doctor android run-flow .\examples\android_apk_cases\post_image_text_dry_run\input\flow.yml --out .\android_run
failure-doctor android replay .\android_run --out .\android_replay
failure-doctor android diagnose .\examples\android_apk_cases\permission_dialog_blocked\input --out .\android_diag
failure-doctor collect --adapter android-apk --input .\examples\android_apk_cases\permission_dialog_blocked\input --out .\android_pack
failure-doctor diagnose .\android_pack --adapter android-apk --out .\android_diag2
```

## Safety Boundary

- Local-only by default.
- Flow execution is dry-run by default.
- Final-submit steps are blocked unless a human approval id is explicitly
  present.
- Coordinates are allowed only as fallback evidence, not the primary locator.
- The adapter does not upload screenshots, call external OCR, read private app
  directories, read device contacts/SMS/browser profiles, modify APKs, or change
  device security posture.
- If a workflow is not authorized, stop and collect only shareable evidence.

## Locator Preference

Prefer stable locators in this order:

1. `resource_id`
2. `accessibility_id` / `content_desc`
3. visible `text`
4. class hierarchy
5. XPath
6. OCR/image fallback
7. coordinate fallback

Coordinates should remain a last-resort fallback because screen density,
viewport, keyboard state, and device orientation can drift.
