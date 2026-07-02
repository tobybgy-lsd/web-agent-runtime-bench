# Agent Failure Doctor v4.2.0 - Plugin SDK & Adapter Ecosystem Pack

v4.2.0 adds a local-only Plugin SDK for extending Agent Failure Doctor while
keeping the public safety boundary intact.

## What changed

- `failure-doctor plugin scaffold/validate/inspect/install/enable/disable/list/run/export/audit`
- Plugin manifest model: `failure_doctor_plugin/v1`
- Plugin types:
  - framework-adapter
  - evidence-adapter
  - diagnosis-rule
  - industry-pack
  - console-extension
  - ci-extension
  - kb-pattern
  - reasoning-tool
  - report-exporter
  - validation-pack
- Permission model with network, shell, raw evidence, and project-write access
  blocked by default.
- Policy sandbox with path and sensitive-location guards.
- Plugin registry and append-only local audit log.
- Candidate-only plugin runner.
- `diagnose --plugin`, `collect --plugin`, console plugin status, CI sanitized
  plugin summary, and agent-bootstrap plugin workflow integration.
- P98 pillars:
  - `plugin_sdk_ecosystem`
  - `plugin_security_sandbox`
  - `adapter_extension_api`

## Reproduce

```powershell
python -m pip install agent-failure-doctor==4.2.0
failure-doctor plugin --help
failure-doctor plugin scaffold --type framework-adapter --name toy_adapter --out .\plugins\toy_adapter
failure-doctor plugin validate .\plugins\toy_adapter
failure-doctor plugin install .\plugins\toy_adapter --workspace .\.failure-doctor-plugins
failure-doctor plugin enable toy_adapter --workspace .\.failure-doctor-plugins
```

## Safety

Plugins are disabled by default. Every plugin must have
`plugin_manifest.json`, declare permissions, pass validation before install, and
pass validation before enable. Plugin output is a candidate only; the core
validator remains final authority.

Blocked by default:

- network access
- shell execution
- raw evidence access
- broad project writes
- browser profile access
- credential store access
- external uploads
- private training or solver content
- unsafe recommendations

## Validation

- `plugin_sdk_ecosystem_validation.json`: pass, 235 synthetic local cases
- `p98_master_gate.json`: pass
- External API calls: 0
- Telemetry calls: 0
- Private solution leaks: 0
- Forbidden output count: 0
- Real platform access count: 0

## Known limits

The v4.2 SDK is a safe extension substrate. It does not grant plugins authority
to override final diagnosis, bypass safety gates, apply patches automatically,
or access raw/private/local-sensitive data without explicit future governance
work.
