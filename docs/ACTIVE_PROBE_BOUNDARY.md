# Active Probe Boundary

Agent Failure Doctor remains local-first. It does not run active network probes
as part of `diagnose`, `collect`, `watch`, `plan`, `verify`, or `sanitize`.

Use this document when you have already produced a sanitized local probe report
from an authorized environment and want to attach it to a failure pack.

## Supported Evidence File

Place a user-supplied `probe_report.json` in the failed-run folder:

```json
{
  "schema_version": "failure-doctor/probe-report/v1",
  "network_access": "performed_by_user_before_diagnosis",
  "transport": {
    "tls_alpn_fingerprint_mismatch": true,
    "alpn": "http/1.1",
    "browser_alpn": "h2",
    "http_version": "1.1",
    "browser_http_version": "2",
    "ja3_hash": "redacted-or-truncated"
  },
  "ip_reputation": {
    "classification": "uncertain"
  }
}
```

Then run:

```powershell
failure-doctor diagnose .\failed_run --out .\report
```

## What The Tool May Conclude

The probe report can support diagnosis such as:

- `tls_alpn_fingerprint_mismatch`
- `transport_fingerprint_risk`

The expected next action is evidence-based triage:

- Standard HTTP client and browser transport fingerprints are inconsistent.
- Collect sanitized TLS / ALPN / HTTP version evidence.
- Confirm whether an authorized API, official SDK, compliant export, or
  platform-approved integration exists.
- Do not misclassify transport evidence as selector, storage, or proxy failure.
- Stop automation when authorization or platform terms are unclear.

## What This Project Does Not Do

Agent Failure Doctor does not provide:

- default active network probes
- CAPTCHA bypass
- bot evasion
- fingerprint spoofing
- protected-signature cracking
- transport impersonation instructions
- proxy or account rotation guidance
- real-platform scraping playbooks

If you need to run active probes for a local lab or authorized environment, keep
that tooling private and provide only sanitized `probe_report.json` evidence to
Agent Failure Doctor.
