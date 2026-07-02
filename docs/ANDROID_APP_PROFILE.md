# Android App Profile

`android_app_profile.json` describes an authorized local Android automation target.

Required defaults:

- `authorized_target: true`
- `dry_run_default: true`
- `allow_final_submit_default: false`

Commands:

```powershell
failure-doctor android-pro profile init --package com.example.mock --out .\android_profile
failure-doctor android-pro profile validate --profile .\android_profile\android_app_profile.json
```
