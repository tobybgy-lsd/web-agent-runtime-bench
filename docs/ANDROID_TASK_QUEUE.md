# Android Task Queue

The Android Pro queue provides local checkpoint metadata for repeatable dry-run workflows.

```powershell
failure-doctor android-pro queue init --out .\queue
failure-doctor android-pro queue run --queue .\queue\android_task_queue.json --flow .\flow.yml --out .\queue_result
```
