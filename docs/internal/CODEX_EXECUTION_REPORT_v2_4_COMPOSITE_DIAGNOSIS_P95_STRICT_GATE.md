# Codex Execution Report: v2.4 Composite Diagnosis P95 Strict Gate

Date: 2026-06-29

## Scope

Implemented the v2.4 composite diagnosis layer for Agent Failure Doctor. The goal was to move from single-label diagnosis toward a deterministic multi-candidate failure lifecycle:

- extract sanitized evidence nodes
- collect multiple diagnosis candidates
- build an evidence graph
- choose primary, blocking, secondary, and downstream failures
- preserve repair order through plan and verify outputs
- keep all outputs local-first and safety bounded

This pack does not add bypass guidance, CAPTCHA solving, fingerprint spoofing, private-target scraping, or external AI upload behavior.

## Main Changes

- Added composite diagnosis modules:
  - `tools/failure_artifacts/evidence_nodes.py`
  - `tools/failure_artifacts/candidates.py`
  - `tools/failure_artifacts/evidence_graph.py`
  - `tools/failure_artifacts/causal_policy.py`
  - `tools/failure_artifacts/composite.py`
- Integrated composite public fields into `failure_doctor diagnose` reports.
- Preserved legacy single-label behavior for older validation runners where needed.
- Added schemas:
  - `schemas/composite_diagnosis.schema.json`
  - `schemas/evidence_graph.schema.json`
  - `schemas/composite_validation_result.schema.json`
- Added local-only strict fixtures:
  - 120 composite family cases
  - 40 adversarial composite cases
- Added validation runner:
  - `python -m tools.validation.run_composite_diagnosis_p95_strict_validation`

## Verification Evidence

Fresh verification run from `D:\WebAgentRuntimeBench-GitHub`:

```text
python -m unittest discover -s tests -p "test_*.py"
Ran 291 tests in 43.274s
OK
```

```text
python -m tools.validation.run_composite_diagnosis_p95_strict_validation
composite diagnosis P95 strict: 160/160 primary, 160/160 repair-order, forbidden_outputs=0, status=pass
```

```text
python -m tools.validation.run_validation_hardening
validation hardening: 10/10 tracks pass, regression_backlog=38, overall_gate=pass
```

```text
python -m tools.validation.run_real_trace_validation
real trace validation: 30/30 reasonable, 30/30 exact, forbidden_outputs=0
```

```text
python -m tools.validation.run_cross_framework_validation
Cases: 42
Reasonable category match: 42
Actionable next action: 42
Fix plan valid: 42
Forbidden output count: 0
Severe misclassification: 0
```

```text
python -m tools.validation.run_spiderbuf_inspired_validation
spiderbuf-inspired validation: 10/10 reasonable, 10/10 fix plans, 10/10 verification correct, forbidden_outputs=0
```

```text
python -m tools.validation.run_resolution_validation
resolution validation: 12/12 correct, forbidden_outputs=0
```

```text
python -m tools.validation.run_applied_scenario_validation
applied scenario validation: 18/18 reasonable, 18/18 fix plans, 18/18 verification correct, forbidden_outputs=0
```

```text
python -m tools.validation.run_external_public_reference_validation
external public reference validation: 20/20 reasonable, 20/20 actionable, forbidden_outputs=0
```

```text
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
SMOKE TEST: PASS
```

```text
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
SAFETY SCAN: PASS
```

## Safety Boundary

The pack keeps anti-bot/access-control handling diagnostic and compliance-oriented only:

- identify likely access-control or rate-limit boundary
- recommend authorized access paths, official APIs, manual export, or stopping when authorization is unclear
- avoid evasion, credential extraction, CAPTCHA bypass, fingerprint spoofing, or signature cracking guidance

## Known Limits

- Composite reasoning is deterministic and evidence-bound; it does not perform free-form LLM inference.
- Evidence graph edges are curated causal policies, not learned from private user data.
- Validation fixtures are local and sanitized; broader ecosystem maturity still depends on external users, issues, and long-term feedback.
