# Integrations

Agent Failure Doctor integrations turn existing automation artifacts into the same failure-pack layout consumed by `failure-doctor diagnose`.

## Playwright

```powershell
failure-doctor collect-playwright .\test-results --out .\failure_pack
failure-doctor diagnose .\failure_pack --out .\report
```

The collector looks for `trace.zip`, error logs, console logs, `network.json`, and screenshots.

## Generic Logs

```powershell
failure-doctor pack-logs .\raw_logs --out .\failure_pack
failure-doctor diagnose .\failure_pack --out .\report
```

Use this when you have loose `error.log`, `console.txt`, `network.json`, screenshots, or a user description.

## browser-use / Browser Agent

```python
from integrations.browser_use.adapter import convert_browser_use_run

convert_browser_use_run("agent_history.json", "failure_pack")
```

Then run:

```powershell
failure-doctor diagnose .\failure_pack --out .\report
```

## GitHub Actions

See [GITHUB_ACTION_USAGE.md](GITHUB_ACTION_USAGE.md) for a workflow snippet that runs `failure-doctor diagnose` and uploads the report with `upload-artifact`.

All integrations are local-first and only normalize files you already have. They do not connect to third-party platforms.

