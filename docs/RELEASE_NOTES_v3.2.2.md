# Agent Failure Doctor v3.2.2 - Spiderbuf-Inspired Safe Diagnostics Patch

v3.2.2 is a patch release for the v3.2 Auto Collector line. It ships the safe
diagnostic improvements that landed on `main` after v3.2.1.

## Quick Install

```powershell
python -m pip install agent-failure-doctor
python -m pip install --upgrade agent-failure-doctor
failure-doctor --help
```

PyPI: [https://pypi.org/project/agent-failure-doctor/](https://pypi.org/project/agent-failure-doctor/)

## What changed

- Promoted the Spiderbuf-inspired public-safe validation pack from 10 to 17 local synthetic cases.
- Added `data_poisoning_decoy_response` diagnosis for HTTP 200 responses that look valid but fail trusted/canary evidence checks.
- Added `header_normalization_evidence_gap` diagnosis when framework logs normalize raw transport/header evidence before inspection.
- Added `stateful_session_lifecycle_anomaly` diagnosis for periodic 401/session refresh failures in long-running collection.
- Added public-safe regression cases for JA3/HTTP2/client hints fingerprint risk, HMAC signature triage, slider trajectory behavioral risk, and MFA risk-login redirects.
- Updated validation ledgers to 17/17 reasonable classification, 17/17 fix-plan validity, 17/17 verification correctness, and 0 forbidden outputs.

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
