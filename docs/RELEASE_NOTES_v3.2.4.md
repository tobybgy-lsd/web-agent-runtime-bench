# Agent Failure Doctor v3.2.4 - Offline Probe Evidence Boundary Patch

## Install

```powershell
python -m pip install agent-failure-doctor
failure-doctor --help
```

PyPI: <https://pypi.org/project/agent-failure-doctor/>

## What changed

- Added `probe_report.json` as a recognized offline evidence input for
  user-supplied, sanitized active-probe summaries.
- Added transport probe evidence mapping for `tls_alpn_fingerprint_mismatch`
  and `transport_fingerprint_risk` without adding any default network probing.
- Added `docs/ACTIVE_PROBE_BOUNDARY.md` to document that active probes must stay
  opt-in and external to the public diagnosis flow.
- Fixed the README language-switch link and documented `probe_report.json` in
  the accepted input list.

## Reproduce

```powershell
python -m pip install agent-failure-doctor
failure-doctor diagnose .\examples\failed_runs\proxy_network_error --out .\report
```

For offline probe evidence, place a sanitized `probe_report.json` in a failed
run folder and run:

```powershell
failure-doctor diagnose .\failed_run --out .\report
```

## Safety

- No default active network probes.
- No browser fingerprint spoofing guidance.
- No transport impersonation guidance.
- No CAPTCHA bypass, bot evasion, credential extraction, protected-signature
  cracking, proxy rotation, or account rotation guidance.
- Forbidden output count remains expected at 0.

## Known limits

- `probe_report.json` is evidence only; the tool does not verify the probe
  source or perform external measurements itself.
- IP reputation labels should remain conservative. If evidence is thin or
  ambiguous, prefer `uncertain` over claiming a safe residential source.
- JA3 string and JA3 hash should be kept distinct in user-supplied evidence.
