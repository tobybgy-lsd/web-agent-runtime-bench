# Changelog

## v1.1.0

- Added Applied Scenario Demo Pack.
- Added six local-only business automation failure demo families:
  - hot product collection
  - live commerce monitoring
  - ecommerce listing automation
  - authorized content publishing workflow
  - GUI / RPA data bridge
  - ERP-to-ecommerce sync
- Added 18 before/after applied scenario cases.
- Added `tools.validation.run_applied_scenario_validation`.
- Added applied scenario validation dashboard output:
  - 18/18 reasonable classifications
  - 18/18 valid fix plans
  - 18/18 correct verification statuses
  - 0 forbidden outputs
- Added resume/interview notes for positioning the project as a failure diagnosis and repair verification layer.
- No real-platform scraping, no automated posting to real platforms, no anti-bot bypass.

## v1.0.0

- Added Failure Resolution Loop:
  - `failure-doctor plan`
  - `failure-doctor verify`
  - fix plan generation
  - before/after resolution verification
  - regression case generation
- Added `fix_plan/v1` and `verification_report/v1` schemas.
- Added 12 local resolution validation cases.
- Resolution validation:
  - 12/12 correct verification statuses
  - 12/12 actionable next steps
  - 0 forbidden outputs
- Anti-bot risk remains identification and compliant routing only.

## v0.8.0

- Added a 131-record source ledger:
  - 50 `real_public_issue`
  - 10 `official_doc_pattern`
  - 71 `public_inspired_sanitized`
- Added 30 native Playwright-generated `trace.zip` fixtures.
- Added real trace semantic validation runner.
- Added native-trace validation coverage for storage/context, route/HAR, shadow DOM, website-change, environment, and anti-bot risk routing.
- Real trace validation:
  - 30/30 reasonable classification
  - 30/30 exact subtype match
  - 0 forbidden outputs
- Added external held-out validation:
  - 10 public-source held-out records
  - 9/10 reasonable classification
  - 10/10 actionable next action
  - 0 forbidden outputs
- GitHub Actions:
  - Ubuntu / macOS / Windows unit tests
  - Windows benchmark / smoke / safety

## v0.6.0

- Added Website Change diagnosis layer.
- Added Anti-Bot Risk identification and compliant routing layer.
- Added 50 public-inspired sanitized Website Change / Anti-Bot Risk corpus records.
- Added independent v0.6 routing validation ledger: 50/50 reasonable classifications, 50/50 safe next actions, 0 forbidden outputs.
- Added `failure_layer` and `safe_next_action` fields to Agent Failure Doctor output.
- Added safety tests to ensure anti-bot risk prompts do not provide bypass guidance.

## v0.4.0

- 150 public-inspired / sanitized validation records with traceable public URLs
- 97.3% reasonable classification
- 94.7% actionable next_action
- 170 tests
- local-first diagnosis
- safety scan
- no CAPTCHA bypass / no bot evasion boundary

## v0.3.0

- Real User Input Pack
- Actionable Report
- Codex fix prompt
- input_summary.json
- missing_evidence
- evidence_priority
