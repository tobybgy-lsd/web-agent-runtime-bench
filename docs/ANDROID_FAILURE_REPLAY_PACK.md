# Android Failure Replay Pack

Replay packs are sanitized local bundles for reproducing Android automation failures from evidence metadata.

```powershell
failure-doctor android-pro replay-pack create --run .\failed_run --out .\replay_pack
```

Raw private app data, credentials, browser profiles, device stores, and external uploads are excluded.
