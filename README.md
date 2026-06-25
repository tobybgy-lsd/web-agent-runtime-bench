# WebAgentRuntimeBench

**Your web scraper failed. You don't know why. This tool tells you.**

WebAgentRuntimeBench classifies web automation failures, generates evidence-backed
reports, and converts real failures into regression tests — so you never debug the
same problem twice.

```bash
python tools/warb.py diagnose examples/failures/seed_004_auth_expiry/failure_artifact.json
```

```
Failure type:  auth_expiry
Confidence:    0.84

Evidence:
  - HTTP 200 but page contains <input type="password">
  - URL redirected from /products to /login
  - Expected fields title/price missing from output

Suggested fix:
  - Refresh authenticated session before scraping
  - Add preflight login-state check
  - Re-run with valid storage_state

Regression case saved: failure_corpus/sanitized/auth_001/
```

No network required. No API keys. No credentials captured.

---

## What it does

| Problem | What warb does |
|---|---|
| Playwright script crashes | Classifies the root cause in seconds |
| Scrapy spider returns empty | Detects response shape change or auth expiry |
| Node.js chokes on `window` | Identifies missing browser API, suggests shim |
| Fixed a bug, broke something else | Regression suite catches it in CI |
| Same bug keeps coming back | Every real failure becomes a test case |

---

## Quickstart

**Requirements:** Python 3.10+, Node.js 18+

```bash
git clone https://github.com/tobybgy-lsd/web-agent-runtime-bench
cd web-agent-runtime-bench

# Diagnose a failure
python tools/warb.py diagnose examples/failures/seed_004_auth_expiry/failure_artifact.json

# Run full benchmark suite
python tools/benchmark/run_benchmark.py --out-dir sample_run/benchmark --node node
```

---

## Failure types detected

| Type | Example | Detected from |
|---|---|---|
| `runtime_api_missing` | `window is not defined` | stderr, console log |
| `network_http_error` | 403, 429, 503 | status code, response |
| `response_shape_change` | expected field `price` missing | schema diff |
| `auth_expiry` | 200 but got login page | HTML snapshot, URL |
| `captcha_or_bot_wall` | Cloudflare challenge page | HTML markers |

---

## Submit a failure, get a diagnosis

Have a failed Playwright/Scrapy/requests run? Send it, get back a free diagnosis report.

**What to send** (no credentials, no tokens needed):

```
error.log          # the error message or stack trace
snapshot.html      # the page HTML at time of failure (sanitized)
screenshot.png     # optional but helpful
network.json       # optional: network log
expected_schema.json  # what fields you expected
actual_output.json    # what you actually got
notes.md           # what you were trying to do
```

→ [Open a GitHub issue](https://github.com/tobybgy-lsd/web-agent-runtime-bench/issues/new?template=failure-artifact.yml)

---

## For AI-assisted debugging

The failure artifacts and diagnosis reports are structured for direct use with
Codex, Claude, or any coding assistant. Instead of pasting raw error logs,
pass the diagnosis report:

```
Here is a structured failure diagnosis: [diagnosis.md]
Please generate a fix for the Playwright script.
```

The report includes: failure type, confidence, evidence, suggested fix direction,
and a repair prompt template.

---

## Architecture

```
Your failed run (Playwright / Scrapy / requests)
        ↓
warb collect    →  failure_artifact.json  (unified schema)
        ↓
warb diagnose   →  diagnosis.json + diagnosis.md + repair_prompt.md
        ↓
warb report     →  diagnosis_report.html  (shareable)
        ↓
warb regression →  sanitized synthetic test case added to corpus
        ↓
CI benchmark    →  regression never recurs
```

---

## Safety boundary

✅ Allowed:
- Your own failure logs and HTML snapshots
- Sanitized local artifacts (no credentials)
- Synthetic local mock cases
- Local Node.js subprocess execution

❌ Never:
- Real platform signatures or tokens
- Network requests to real sites
- Credentials, cookies, Authorization headers
- CAPTCHA bypass or anti-bot evasion

---

## Standard benchmark

The repo includes a synthetic benchmark suite for testing runtime diagnosis
capabilities without any real-world targets.

```bash
python tools/benchmark/run_benchmark.py --out-dir sample_run/benchmark --node node
```

See [docs/benchmark_tasks.md](docs/benchmark_tasks.md) for task definitions and
[sample_reports/benchmark_ci_report_sample.md](sample_reports/benchmark_ci_report_sample.md)
for a sample CI report.

---

## Contributing

See [docs/submit_failure_pack.md](docs/submit_failure_pack.md) to submit a
sanitized failure artifact.

MIT License
