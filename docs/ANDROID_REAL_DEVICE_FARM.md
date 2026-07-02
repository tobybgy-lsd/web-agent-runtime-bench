# Android Real Device Farm

Agent Failure Doctor v5.3 adds a local-only Android device farm layer for authorized
Android automation operations.

The default farm is mock-first and dry-run. It records only device identifiers,
Android API level, screen size, DPI, status, and tags. It does not store account
credentials, tokens, cookies, private app data, browser profiles, or screenshots.

```powershell
failure-doctor android-ops farm init --out .\android_farm
failure-doctor android-ops farm discover --farm .\android_farm --out .\device_inventory
failure-doctor android-ops farm status --farm .\android_farm
```

All farm actions write a local audit log. Final submit and business mutation remain
blocked by default.

