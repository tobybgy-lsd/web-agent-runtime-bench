# Android Device Lease And Recovery

Device leases prevent two local tasks from using the same Android device at once.

```powershell
failure-doctor android-ops device lease --farm .\android_farm --device mock-emulator-5554 --task-id task_001
failure-doctor android-ops device release --farm .\android_farm --device mock-emulator-5554 --task-id task_001
```

Recovery supports only controlled strategies: `soft-reset`, `app-restart`,
`session-clean`, and `mock-recovery`. It does not factory reset, root, hook, modify
APKs, or read private data.

