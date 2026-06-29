# Integrations

## Cross-Framework Adapter

Use `failure-doctor adapt` when the failure came from Selenium, Puppeteer, Cypress, Scrapy, requests, or httpx logs rather than a Playwright `trace.zip`.

```powershell
failure-doctor adapt .\my_failed_run --framework selenium --out .\failure_pack
failure-doctor diagnose .\failure_pack --out .\report
failure-doctor plan .\report --out .\fix_plan
```

Supported values:

```text
selenium | puppeteer | cypress | scrapy | requests | httpx | auto
```

The adapter writes:

```text
failure_pack/
|-- error.log
|-- console.txt
|-- network.json
|-- user_description.txt
|-- framework_metadata.json
|-- input_summary.json
`-- README_FOR_REVIEWER.md
```

This is a log normalization layer. It does not run the source framework, open browsers, call external services, upload artifacts, or connect to real platforms.

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
