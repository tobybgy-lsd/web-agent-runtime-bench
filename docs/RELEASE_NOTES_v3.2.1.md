# Agent Failure Doctor v3.2.1 - Complex Scraper Diagnostic Patch

v3.2.1 is a patch release for the v3.2 Auto Collector line. It ships the safe
diagnostic improvements that landed on `main` after v3.2.0.

## Quick Install

```powershell
python -m pip install agent-failure-doctor
python -m pip install --upgrade agent-failure-doctor
failure-doctor --help
```

PyPI: [https://pypi.org/project/agent-failure-doctor/](https://pypi.org/project/agent-failure-doctor/)

## What changed

- Added `client_hints_missing` diagnosis for missing Client Hints / Sec-CH-UA metadata.
- Added `honeypot_data_mismatch` diagnosis for plausible but untrusted data caused by browser metadata mismatch.
- Added `mfa_risk_login_required` diagnosis for rate-limit to MFA / risk-login flows.
- Added `service_worker_cache_interference` diagnosis for Service Worker or cache-layer stale content.
- Added `sse_stream_detected` diagnosis so SSE/EventSource streams are not mistaken for binary payloads or plain JSON.
- Added `proxy_header_leak` diagnosis for Via / X-Forwarded-For proxy metadata evidence.
- Improved MD5 vs HMAC signature triage for timestamp/salt signature failures.
- Added regression tests for the Spiderbuf-inspired composite-risk cases.

## Safety

- Diagnosis-only public output.
- Forbidden outputs remain disallowed by the local safety scan.
- No CAPTCHA bypass guidance.
- No bot evasion guidance.
- No MFA bypass guidance.
- No credential extraction.
- No private solver or local training helper publication.
- Local `tools/spiderbuf/` training helpers remain ignored and out of the public package boundary.

## Reproduce

```powershell
python -m pip install --upgrade agent-failure-doctor
python -m unittest discover -s tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

## Known limits

- This release improves failure classification; it does not add bypass, solver, or source-code repair automation.
- The complex scraper diagnostics are evidence labels and safe next-action guidance, not authorization to access protected systems.
