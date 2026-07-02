# Desktop RPA Adapters

Agent Failure Doctor v4.4 supports local-only mock RPA artifact adapters for
UiPath-style and Yingdao-style logs. The adapters normalize local logs into
diagnosis evidence and never control a real desktop application.

```powershell
failure-doctor adapter rpa normalize --input .\rpa_logs --out .\rpa_normalized
failure-doctor adapter rpa diagnose --input .\rpa_logs --out .\rpa_report
```

Supported public-safe subtypes include `rpa_selector_drift`,
`rpa_window_focus_lost`, `rpa_control_not_found`,
`rpa_image_match_low_confidence`, `rpa_permission_dialog_blocked`, and
`rpa_timeout_waiting_window`.
