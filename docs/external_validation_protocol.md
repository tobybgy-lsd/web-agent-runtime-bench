# External Validation Protocol

Agent Failure Doctor distinguishes author-built validation from external sample validation.

External validation means a sanitized failure case is received or referenced, run with the current released version before rule tuning, recorded, and then tracked in a dashboard.

## Case Types

- `public_external_issue`: a sanitized failure case submitted through this repository's issue tracker
- `external_public_reference`: a traceable public issue, Q&A, or discussion from another project
- `public_inspired_sanitized`: a reconstructed pattern inspired by public reports; useful for tests, but not counted as an external-user case

## First-Run Rule

For each accepted external case:

1. Create a stable id such as `EXT-2026-0001`.
2. Save metadata in `validation/external_cases/<case_id>.json`.
3. Run the current version before changing diagnosis rules.
4. Save the generated report under `validation/external_reports/<case_id>/`.
5. Record the first-run category, subtype, result, next-action quality, and forbidden-output status.
6. If a miss is later fixed, add a regression test and keep the first-run result unchanged.

## Safety Boundary

Safety rule: Anti-bot risk handling is identification and compliant routing only. Reports and fix prompts must not provide instructions for challenge bypass, bot evasion, fingerprint spoofing, dynamic signature cracking, platform access-control defeat, IP-pool rotation, account-pool use, or CAPTCHA automation.

Safe outputs include confirming authorization, using an official API, using an authorized export, reducing request volume, contacting the platform owner, manual review, or stopping unclear runs.

## Reproduce

```powershell
python -m tools.validation.run_external_validation
```

The runner must succeed when there are zero accepted external cases. Zero is a valid starting point and is better than counting templates as external validation.
