# Codex Execution Report - v3.6.0 Regulated Visual Full-Chain

Date: 2026-07-02

## Scope

Implemented Agent Failure Doctor v3.6.0 as the Regulated Industry & Pure Visual Agent Full-Chain Evaluation Pack.

Public scope stays diagnosis, evidence, reporting, safety gates, and local-only evaluation. Private training artifacts, challenge solvers, flags, and bypass recipes are not packaged or published.

## Added

- `failure-doctor regulated-eval --suite finance|government|healthcare|common|all --out <dir>`
- `failure-doctor full-chain-eval --input <failed_run_or_report> --out <dir>`
- Regulated industry evaluator for finance, government, healthcare, and common workflow cases.
- Full-chain agent workflow evaluator for collect, diagnose, plan, verify, sanitize/share, AI handoff, OCR, visual, and regulated stages.
- v3.6 validation outputs:
  - `validation/regulated_industry_validation.json`
  - `validation/full_chain_agent_evaluation.json`
  - updated `validation/visual_agent_runtime_validation.json`
  - updated `validation/p98_master_gate.json`
- P98 pillars:
  - `regulated_industry_workflow_pack`
  - `visual_agent_runtime_observability`
  - `full_chain_agent_evaluation`
- Docs:
  - `docs/REGULATED_INDUSTRY_WORKFLOW_PACK.md`
  - `docs/PURE_VISUAL_AGENT_RUNTIME_EVALUATION.md`
  - `docs/FULL_CHAIN_AGENT_EVALUATION.md`
  - `docs/RELEASE_NOTES_v3.6.0.md`

## Validation Evidence

Fresh local verification:

```text
python -m unittest discover -s tests -p "test_*.py"
Ran 431 tests in 82.577s
OK
```

```text
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
SAFETY SCAN: PASS
```

```text
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
SMOKE TEST: PASS
```

```text
python -m twine check dist/*
agent_failure_doctor-3.6.0-py3-none-any.whl: PASSED
agent_failure_doctor-3.6.0.tar.gz: PASSED
```

```text
python -m tools.validation.run_package_private_content_scan
status: pass
private_content_found: 0
forbidden_output_count: 0
private_solution_leak_count: 0
real_platform_access_count: 0
```

```text
python -m tools.validation.run_p98_master_gate
version: v3.6.0
overall_status: pass
controlled_maturity_score: 98
current_stable_line: v3.6.0
global_forbidden_output_count: 0
global_private_solution_leak_count: 0
global_real_platform_access_count: 0
```

Clean wheel install was verified from `dist\agent_failure_doctor-3.6.0-py3-none-any.whl`; the installed `failure-doctor` command exposes `regulated-eval`, `visual-runtime`, and `full-chain-eval`.

Manual v3.6 smoke commands were verified:

- `regulated-eval --suite finance`: pass, 60 cases
- `regulated-eval --suite government`: pass, 60 cases
- `regulated-eval --suite healthcare`: pass, 60 cases
- `visual-runtime diagnose` on `stale_screenshot_action`: subtype `stale_screenshot_action`
- `visual-runtime compare`: generated comparison CSV/Markdown/JSON artifacts
- `full-chain-eval`: pass

## Safety Boundary

- Cloud OCR/VLM/LLM calls remain disabled by default.
- External OCR/VLM upload counters remain zero in validation.
- Regulated workflows are mock/local evaluation only.
- Reports use disclaimers and do not provide legal, medical, financial, or regulatory advice.
- Public package private-content scan passed after building wheel and sdist.

## Notes

One full-test run failed while running multiple validation-heavy commands in parallel because Windows returned `OSError 22` while a validation JSON file was being rewritten. The same OCR validation test passed standalone, and the full test suite passed when run serially. Release verification should keep validation writers serial.
