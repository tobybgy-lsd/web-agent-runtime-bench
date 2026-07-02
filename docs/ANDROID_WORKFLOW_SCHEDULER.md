# Android Workflow Scheduler

The scheduler creates local dry-run task assignments across available farm devices.
It respects device leases, writes checkpoints, and does not repeat successful tasks.

```powershell
failure-doctor android-ops scheduler plan --farm .\android_farm --queue .\bound_tasks --out .\schedule_plan
failure-doctor android-ops scheduler run --plan .\schedule_plan --out .\ops_run
```

Uncertain tasks should be routed to manual review.

