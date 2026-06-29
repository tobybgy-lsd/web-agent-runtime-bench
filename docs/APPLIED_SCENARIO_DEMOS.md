# Applied Scenario Demos

The Applied Scenario Demo Pack shows how Agent Failure Doctor handles realistic business automation failure evidence while staying local-only and mock-only.

These demos are not a production commerce, content publishing, GUI bridge, or ERP system. They are sanitized failure diagnosis packs that exercise:

- `failure-doctor diagnose`
- `failure-doctor plan`
- `failure-doctor verify`
- regression case metadata

## What Each Scenario Contains

Each scenario under `examples/applied_scenarios/` includes:

- `README.md`
- local mock app/API/input files
- top-level `failed_run/` and `rerun_after_fix/` for a quick manual demo
- `cases/*/failed_run/`
- `cases/*/rerun_after_fix/`
- `expected_diagnosis.json`
- `expected_fix_plan.json`
- `expected_verification.json`
- `regression_case.json`

## Scenarios

| Scenario | What It Demonstrates |
|---|---|
| `01_hot_product_collector` | selector drift, response shape changes, pagination changes |
| `02_live_commerce_monitor` | WebSocket/CDP disconnects, event schema changes, navigation races |
| `03_ecommerce_listing_automation` | file chooser upload failures, SKU selector drift, storage-state login redirects |
| `04_content_publishing_workflow` | rich-text iframe handling, asset upload failures, manual approval or permission blocks |
| `05_gui_data_bridge` | download not saved, popup/new page handling, virtualized table extraction |
| `06_erp_ecommerce_sync` | ERP-like field mapping changes, permission blocks, rate limiting |

## Run the Validation

```powershell
python -m tools.validation.run_applied_scenario_validation
```

Current expected result:

```text
18/18 reasonable classifications
18/18 valid fix plans
18/18 correct verification statuses
0 forbidden outputs
```

## Safety Boundary

All applied scenario demos are local-only mock workflows. They do not access real commerce platforms, real live platforms, real content platforms, or real ERP systems.

The demos do not include real cookies, tokens, authorization headers, accounts, customer data, phone numbers, identity numbers, private URLs, or production store data.

For platform-risk cases, the expected output is identification and compliant routing only: confirm authorization, use an official API or authorized export, request manual review, contact the platform owner, or stop unclear automation.
