# Codex Execution Report: v4.2 Plugin SDK

## 1. Goal

Implement Agent Failure Doctor v4.2 Plugin SDK & Adapter Ecosystem Pack without
publishing local private training, solver, FLAG, hook, VMP, challenge-pass, or
trajectory content.

## 2. Starting Version

v4.1.0 Enterprise Governance & Role-Based Console Pack.

## 3. New CLI

- `failure-doctor plugin list`
- `failure-doctor plugin scaffold`
- `failure-doctor plugin validate`
- `failure-doctor plugin inspect`
- `failure-doctor plugin install`
- `failure-doctor plugin enable`
- `failure-doctor plugin disable`
- `failure-doctor plugin run`
- `failure-doctor plugin export`
- `failure-doctor plugin audit`

## 4. Plugin SDK Architecture

Added `failure_doctor/plugin/` with manifest loading, permission constants,
validation, scaffold generation, policy sandbox, registry, audit log, candidate
runner, inspector, and CLI integration.

## 5. Plugin Manifest Spec

Plugins require `plugin_manifest.json` using
`failure_doctor_plugin/v1`. Manifest validation checks type, permissions, hooks,
entrypoint, schemas, and safety metadata.

## 6. Plugin Type List

Supported types:

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

## 7. Permission Model

Default allowed permissions:

- read_input_dir
- write_output_dir
- emit_evidence

Network, shell, raw evidence, project writes, browser profile access, credential
store access, and disabling safety gates are blocked by default.

## 8. Hook API

Supported hooks include collection, diagnosis candidate, evidence normalization,
console page, CI summary, KB pattern, reasoning tool, report exporter, and
validation case provider hooks.

## 9. Sandbox Model

v4.2 uses a policy sandbox with path guard, sensitive-location guard,
permission guard, validation guard, audit guard, and fail-closed behavior.

## 10. Scaffold Templates

`failure-doctor plugin scaffold` generates:

- plugin_manifest.json
- plugin.py
- schemas/input.schema.json
- schemas/output.schema.json
- tests/test_plugin.py
- README.md
- FORBIDDEN_ACTIONS.md

## 11. Plugin Validation

`failure-doctor plugin validate` writes:

- plugin_validation_report.json
- plugin_validation_report.md

Unsafe plugins are not installable or enableable.

## 12. Plugin Registry

Plugin workspaces contain:

- plugin_workspace_manifest.json
- registry.json
- audit_log.jsonl
- installed/
- validation_reports/
- exports/

## 13. Integrations

- `diagnose --plugin` attaches candidate-only plugin diagnosis output.
- `collect --plugin` runs a safe adapter candidate path.
- Console exposes plugin status only.
- CI can attach sanitized plugin summary.
- Agent bootstrap writes `plugin_sdk_workflow.md`.
- Enterprise governance remains authoritative for sensitive actions.

## 14. Example Plugins

Added `examples/plugins/` and `templates/plugins/` public-safe local-only
example/template entry points.

## 15. Validation Metrics

`plugin_sdk_ecosystem_validation.json` covers 235 synthetic local cases.

## 16. Safety Counters

- unsafe_plugin_blocked: 30
- external_api_call_count: 0
- private_solution_leak_count: 0
- forbidden_output_count: 0
- real_platform_access_count: 0

## 17. P98 Gate

Added:

- plugin_sdk_ecosystem
- plugin_security_sandbox
- adapter_extension_api

## 18. Verification

Verification commands are run in the release closeout step before tagging or
publishing.

## 19. Release Decision

v4.2.0 may be tagged and published only if unit tests, plugin validation, P98
master gate, P95 core gate, safety scan, package private content scan, build,
twine check, and clean install all pass.

## 20. Remaining Limits

The SDK is an extension substrate, not a marketplace trust system. Plugins
cannot override final diagnosis or safety gates, and high-risk permissions
remain blocked by default.
