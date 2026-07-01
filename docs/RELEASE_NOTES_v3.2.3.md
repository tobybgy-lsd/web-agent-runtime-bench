# Agent Failure Doctor v3.2.3 - TLS/ALPN Safe Diagnostics Patch

v3.2.3 is a patch release for the v3.2 Auto Collector line. It ships public-safe
transport-layer diagnostics that landed on `main` after v3.2.2.

## Quick Install

```powershell
python -m pip install agent-failure-doctor
python -m pip install --upgrade agent-failure-doctor
failure-doctor --help
```

PyPI: [https://pypi.org/project/agent-failure-doctor/](https://pypi.org/project/agent-failure-doctor/)

## What changed

- Added `tls_alpn_fingerprint_mismatch` diagnosis when a standard HTTP client and browser transport path show incompatible TLS/ALPN/HTTP-version evidence.
- Added `transport_fingerprint_risk` diagnosis for broader TLS handshake, ALPN, HTTP version, and client-hints evidence drift.
- Added safe suggestions to collect sanitized TLS/ALPN/HTTP-version evidence, check official APIs / SDKs / compliant exports, and stop automation when authorization is unclear.
- Expanded the Spiderbuf-inspired public-safe validation pack from 25 to 27 local synthetic cases.
- Updated validation ledgers to 27/27 reasonable classification, 27/27 fix-plan validity, 27/27 verification correctness, and 0 forbidden outputs.

## Safety

- Diagnosis-only public output.
- Forbidden outputs remain disallowed by the local safety scan.
- No CAPTCHA bypass guidance.
- No bot evasion guidance.
- No MFA bypass guidance.
- No credential extraction.
- No transport fingerprint impersonation guidance.
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
