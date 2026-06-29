# Codex Execution Report: v1.1 Applied Scenario Demo Pack

Date: 2026-06-29

## Scope

Added Applied Scenario Demo Pack for Agent Failure Doctor v1.1. The goal is to demonstrate local-only business automation failure diagnosis without turning the project into a production commerce, content, GUI, or ERP system.

## Added Scenario Families

| Scenario | Covered Failure Types |
|---|---|
| `01_hot_product_collector` | selector drift, response shape change, pagination change |
| `02_live_commerce_monitor` | CDP/WebSocket disconnect, event schema change, execution context destroyed |
| `03_ecommerce_listing_automation` | file chooser upload, SKU selector drift, storage_state login redirect |
| `04_content_publishing_workflow` | iframe locator, file chooser upload, permission/manual approval block |
| `05_gui_data_bridge` | download not saved, popup/new page handling, virtualized table selector |
| `06_erp_ecommerce_sync` | field mapping change, permission block, rate limit |

## New Artifacts

- `examples/applied_scenarios/`
- `tools/validation/run_applied_scenario_validation.py`
- `validation/applied_scenario_validation.json`
- `docs/APPLIED_SCENARIO_DEMOS.md`
- `docs/RESUME_AND_INTERVIEW_NOTES.md`

## Applied Scenario Validation

```text
18/18 reasonable classifications
18/18 valid fix plans
18/18 correct verification statuses
0 forbidden outputs
```

Command:

```powershell
python -m tools.validation.run_applied_scenario_validation
```

## Local Verification

Completed:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -p "test_*.py"
python -m unittest tests.test_applied_scenario_validation tests.test_applied_scenario_safety
python -m unittest tests.test_public_release_cleanup tests.test_release_trust_pack
python -m tools.validation.run_real_trace_validation
python -m tools.validation.run_external_public_reference_validation
python -m tools.validation.run_resolution_validation
python -m tools.validation.run_applied_scenario_validation
python -m tools.validation.run_external_validation
failure-doctor diagnose examples\applied_scenarios\03_ecommerce_listing_automation\failed_run --out tmp_listing_report
failure-doctor plan tmp_listing_report --out tmp_listing_plan
failure-doctor verify --before examples\applied_scenarios\03_ecommerce_listing_automation\failed_run --after examples\applied_scenarios\03_ecommerce_listing_automation\rerun_after_fix --out tmp_listing_verify
scripts\smoke_test.ps1
scripts\local_safety_scan.ps1
```

Results:

- Installed editable package as `agent-failure-doctor-1.1.0`.
- Full unit suite: `Ran 240 tests ... OK`.
- Real trace validation: `30/30 reasonable, 30/30 exact, forbidden_outputs=0`.
- External public reference validation: `20/20 reasonable, 20/20 actionable, forbidden_outputs=0`.
- Resolution validation: `12/12 correct, forbidden_outputs=0`.
- Applied scenario validation: `18/18 reasonable, 18/18 fix plans, 18/18 verification correct, forbidden_outputs=0`.
- External validation queue: `0/0 reasonable, 0/0 actionable, forbidden_output=0`.
- Listing scenario manual verify: `status=resolved`.
- Smoke test: `PASS`.
- Safety scan: `PASS`.

## Safety Review

The applied scenarios are local-only mock workflows. They do not access real commerce, live, content, GUI, or ERP platforms and do not include real cookies, tokens, authorization headers, accounts, customer data, phone numbers, identity numbers, private URLs, or production store data.

For platform-risk cases, generated next actions must stay compliance-oriented: confirm authorization, use official API or authorized export, complete manual review, contact the platform owner, or stop unclear automation.

## Known Limits

- Scenario fixtures are representative local mocks, not raw private enterprise failure packages.
- Screenshot input remains metadata-only.
- External ecosystem maturity still depends on future user-submitted sanitized cases, issues, and PRs.

## CI

GitHub Actions run: `28345592252`

Commit: `98c7d80 feat: add applied scenario demo pack`

Result: `success`

Passed jobs:

- `unit-tests (windows-latest)`
- `unit-tests (ubuntu-latest)`
- `unit-tests (macos-latest)`
- `benchmark-windows`

The unit-test matrix also ran:

- external validation runner
- external public reference validation
- resolution validation
- applied scenario validation
