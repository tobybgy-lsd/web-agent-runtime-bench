# Android Real Device Replay

Real Device Replay compares failed local run evidence on the same or different
device, but defaults to dry-run replay.

```powershell
failure-doctor android-ops replay --run .\ops_run\failed\task_001 --device mock-emulator-5554 --out .\replay_report
```

Replay does not perform final submit or business mutation by default.

