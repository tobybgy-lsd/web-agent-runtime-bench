# Migration Guide

Use migration dry-runs before changing enterprise workspaces.

```powershell
failure-doctor deploy migrate --workspace .\.failure-doctor-enterprise --from 4.4.0 --to 4.5.0
```

Dry-runs should report planned schema changes and never modify raw artifacts.
