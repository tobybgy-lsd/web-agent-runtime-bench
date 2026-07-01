# Behavioral and Client Hints Evidence Boundary

Agent Failure Doctor v3.2.5 can ingest sanitized, user-supplied evidence about
browser runtime metadata and input-timing telemetry. This is a diagnostic
boundary, not an automation or evasion feature.

## Supported offline inputs

Place either file in a failed-run directory before running `failure-doctor
diagnose`:

```text
browser_runtime_report.json
input_timing_summary.json
```

These files are treated like evidence summaries. Agent Failure Doctor does not
collect them automatically, does not open a browser to gather them, and does not
run active probes as part of diagnosis.

## Public-safe diagnoses

The public package may classify these subtypes:

```text
client_hints_platform_mismatch
browser_header_consistency_risk
keystroke_telemetry_anomaly
zero_interval_input_detected
behavioral_input_risk
```

The recommended output is intentionally limited to:

- treating the issue as a browser/runtime or behavioral consistency risk
- collecting sanitized evidence such as user-agent, Client Hints, navigator
  metadata, HTTP version, and input-timing summaries
- checking for an authorized API, official SDK, documented test hook, compliant
  export, or platform-approved integration
- stopping automation when authorization or platform terms are unclear

## Not included

The public project must not include:

- private challenge solvers
- challenge flags or private target details
- browser stealth implementation recipes
- input mimicry or timing recipes
- CAPTCHA solving or bypass instructions
- anti-bot evasion, fingerprint spoofing, or signature-cracking steps
- default active network, TLS, IP, or browser probes

Keep private training assets local. Only publish generalized, sanitized
diagnostic patterns and safety-preserving tests.
