# Android APK UI Automation Examples

These examples are public-safe, local-only fixtures for the Android APK adapter.
They model evidence normalization, UI-tree parsing, flow validation, diagnosis,
and dry-run replay. They do not include private challenge solutions, account
automation, device pools, root/system modification, or external upload.

Try:

```powershell
failure-doctor android validate-flow .\examples\android_apk_cases\post_image_text_dry_run\input\flow.yml --out .\tmp_android_flow
failure-doctor android dump-ui .\examples\android_apk_cases\ui_tree_basic\input\ui.xml --out .\tmp_android_ui
failure-doctor diagnose .\examples\android_apk_cases\permission_dialog_blocked\input --adapter android-apk --out .\tmp_android_diag
```
