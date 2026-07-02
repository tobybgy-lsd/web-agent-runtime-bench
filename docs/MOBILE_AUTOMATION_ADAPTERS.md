# Mobile Automation Adapters

Agent Failure Doctor v4.4 supports local-only Appium-style mock logs for
mobile automation failure triage.

```powershell
failure-doctor adapter mobile normalize --input .\appium_logs --out .\mobile_normalized
failure-doctor adapter mobile diagnose --input .\appium_logs --out .\mobile_report
```

Supported public-safe subtypes include `mobile_element_not_found`,
`mobile_context_mismatch`, `mobile_permission_dialog_blocked`,
`mobile_network_unstable`, and `mobile_viewport_density_mismatch`.
