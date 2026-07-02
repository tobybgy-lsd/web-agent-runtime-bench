# Agent Failure Doctor CI/CD Integration

v3.8 adds a local-only CI gate for teams that already generate Failure Doctor reports in a test job, RPA job, scraper job, or browser-agent job.

## Commands

```powershell
failure-doctor ci run --input .failure-doctor\report --out .failure-doctor\ci --fail-on high
failure-doctor ci validate --input .failure-doctor\ci --out .failure-doctor\ci_validation
failure-doctor ci templates --out .failure-doctor\templates
```

## Outputs

```text
.failure-doctor/ci/
├── ci_manifest.json
├── ci_summary.json
├── ci_summary.md
├── severity_decision.json
├── gate_decision.json
├── audit_manifest.json
├── open_this_first_ci.md
└── sanitized_artifacts/
```

## Safety Boundary

The CI pack is designed for local runners and sanitized artifacts.

- It does not call external APIs.
- It does not upload raw traces, screenshots, cookies, browser profiles, or environment dumps.
- It blocks private training markers and unsafe recommendation markers before an artifact is shared.
- It is for diagnosis, repair planning, verification, and safe handoff only.

## Templates

`failure-doctor ci templates` writes starting templates for:

- GitHub Actions
- GitLab CI
- Jenkins
- PowerShell local runners

Review the generated files before adding them to a production CI system. Keep raw evidence inside local runner storage unless it has passed sanitize/share review.
