# Playwright Integration

The Playwright collector turns local `test-results` artifacts into an Agent Failure Doctor failure pack.

```powershell
failure-doctor collect-playwright .\test-results --out .\failure_pack
failure-doctor diagnose .\failure_pack --out .\report
```

It looks for `trace.zip`, error logs, console logs, `network.json`, and screenshots. It does not upload artifacts and does not connect to real platforms.

