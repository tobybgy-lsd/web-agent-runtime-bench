# Generic Log Pack Adapter

Use this adapter when a user has a loose folder of logs and screenshots but does not know the Agent Failure Doctor folder layout.

```powershell
failure-doctor pack-logs .\raw_logs --out .\failure_pack
failure-doctor diagnose .\failure_pack --out .\report
```

The adapter normalizes recognized files into `error.log`, `console.txt`, `network.json`, `user_description.txt`, screenshot metadata, and `input_summary.json`.

