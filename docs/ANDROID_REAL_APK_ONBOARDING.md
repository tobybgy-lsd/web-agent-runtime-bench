# Android Real APK Onboarding

Real APK onboarding starts with local evidence and authorization.

```powershell
failure-doctor android-pro onboarding-check --profile .\android_profile\android_app_profile.json --flow .\flow.yml --out .\onboarding
```

Required boundary:

- The target must be owned, authorized, or a mock/training app.
- Workflows remain dry-run unless explicitly reviewed outside the default package behavior.
- No final posting, ordering, payment, trading, account action, or irreversible operation is executed by default.
