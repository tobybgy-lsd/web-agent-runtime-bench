# Agent Failure Doctor v3.8.0 - CI/CD Integration Pack

## Reproduce

```powershell
python -m pip install agent-failure-doctor
failure-doctor --help
failure-doctor ci templates --out .\ci_templates
```

PyPI: <https://pypi.org/project/agent-failure-doctor/>

## What changed

- Added `failure-doctor ci run` for local CI gate generation.
- Added `failure-doctor ci validate` for CI report self-checks.
- Added `failure-doctor ci templates` for GitHub Actions, GitLab CI, Jenkins, and PowerShell starter templates.
- Added `ci_manifest.json`, `ci_summary.md/json`, `severity_decision.json`, `gate_decision.json`, `audit_manifest.json`, and `open_this_first_ci.md`.
- Added `ci_cd_integration` to the P98 master gate.

## Safety

- Local-first by default.
- No external API calls.
- No raw artifact upload.
- No browser profile or credential-store access.
- Private training artifacts and unsafe recommendation markers fail the CI gate.

Forbidden output count remains zero in the validation payload.

## Known limits

- The generated CI templates are starter templates and should be reviewed before production use.
- CI reports are designed for sanitized local artifacts, not raw trace or browser profile upload.
- The gate is a safety and readiness check; it does not replace project-specific test assertions.

## Verification Targets

- `python -m unittest tests.test_ci_cd_integration`
- `python -m tools.validation.run_ci_cd_integration_validation`
- `python -m tools.validation.run_p98_master_gate`
- `python -m tools.validation.run_package_private_content_scan`
- `scripts\local_safety_scan.ps1`
