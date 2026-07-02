# Android Flow Template Library

v5.2.0 includes dry-run templates in `templates/android_flows`.

All templates declare:

- `authorized_target: true`
- `target_kind: mock_app`
- `dry_run_default: true`
- `allow_final_submit: false`

Use:

```powershell
failure-doctor android-pro flow scaffold --template post_image_text_dry_run --out .\flow.yml
failure-doctor android-pro flow lint --flow .\flow.yml --out .\lint
```
