# Codex Execution Report: v2.0 Auto Capture Pack

Date: 2026-06-29

## Scope

Added Auto Capture so users can run a local command through Agent Failure Doctor and automatically collect stdout, stderr, exit code, environment metadata, detected artifact hints, diagnosis, fix plan, and a review-required shareable pack.

This version does not add production scraping, business-system automation, automatic code modification, or anti-bot bypass behavior.

## New Entrypoint

```powershell
failure-doctor run -- <command>
```

Examples:

```powershell
failure-doctor run -- python crawler.py
failure-doctor run -- pytest tests/test_listing.py
failure-doctor run -- playwright test
```

## Output Layout

```text
.failure-doctor/runs/<run_id>/
|-- command.txt
|-- exit_code.txt
|-- stdout.log
|-- stderr.log
|-- environment.json
|-- detected_artifacts.json
|-- input_summary.json
|-- redaction_report.json
|-- safe_to_share.json
|-- diagnosis/
|-- fix_plan/
|-- verification_hint.md
`-- shareable_failure_pack.zip
```

## Local Verification

Final local verification on Windows / PowerShell:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -p "test_*.py"
python -m tools.validation.run_real_trace_validation
python -m tools.validation.run_resolution_validation
python -m tools.validation.run_applied_scenario_validation
python -m tools.validation.run_external_public_reference_validation
python -m tools.validation.run_validation_hardening
scripts\smoke_test.ps1
scripts\local_safety_scan.ps1
```

Results:

- `python -m pip install -e .`: installed `agent-failure-doctor-2.0.0`
- `python -m unittest discover -s tests -p "test_*.py"`: 253 tests passed
- `python -m tools.validation.run_real_trace_validation`: 30/30 reasonable, 30/30 exact, forbidden_outputs=0
- `python -m tools.validation.run_resolution_validation`: 12/12 correct, forbidden_outputs=0
- `python -m tools.validation.run_applied_scenario_validation`: 18/18 reasonable, 18/18 fix plans, 18/18 verification correct, forbidden_outputs=0
- `python -m tools.validation.run_external_public_reference_validation`: 20/20 reasonable, 20/20 actionable, forbidden_outputs=0
- `python -m tools.validation.run_validation_hardening`: 9/9 tracks pass, regression_backlog=38, overall_gate=pass
- `scripts\smoke_test.ps1`: PASS
- `scripts\local_safety_scan.ps1`: PASS
- Failed wrapped command returns the original child exit code
- Failed wrapped command creates diagnosis and fix_plan
- Successful wrapped command records logs and does not force diagnosis
- Bearer token text is redacted from stderr
- `safe_to_share.json` defaults to `safe_to_share=false`

## Safety Boundary

The run wrapper executes only the command the user provides locally. It captures local process output and writes local artifacts. Basic redaction is applied, but the generated pack still requires manual review before sharing.

The tool must not provide challenge bypass, access-control circumvention, credential extraction, account rotation, network rotation, or signature defeat guidance.

## CI

GitHub Actions passed after push:

- Workflow: `benchmark`
- Run id: `28347365006`
- Branch: `main`
- Commit: `0fed31a`
- Result: success
