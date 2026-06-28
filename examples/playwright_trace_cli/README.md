# Playwright Trace CLI Fixture

This directory contains source files for a synthetic Playwright trace adapter example.

It is not a real Playwright trace captured from a website. The test suite zips
these files into a temporary `trace.zip` and runs:

```powershell
python tools\warb.py adapt playwright-trace trace.zip --out sample_run\from_trace
```

Expected diagnosis: `selector_drift`.

Safety:

- Uses `https://example.test/products` only as inert fixture text.
- No browser launch.
- No network replay.
- No cookies, tokens, credentials, or real platform signatures.
