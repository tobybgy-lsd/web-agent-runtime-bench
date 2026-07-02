# Agent Failure Doctor v4.0.0 - Hybrid Evidence Reasoning Pack

v4.0.0 adds a local, evidence-bound reasoning layer.

## Install

```powershell
python -m pip install agent-failure-doctor
failure-doctor --help
```

PyPI: https://pypi.org/project/agent-failure-doctor/

## New Commands

```powershell
failure-doctor reason --input .\report --out .\report\hybrid_reasoning
failure-doctor root-cause --input .\report --out .\root_cause_report
failure-doctor causal-chain --input .\report --out .\causal_chain_report
failure-doctor diagnose .\failed_run --hybrid-reasoning --out .\report
failure-doctor ci diagnose --project .\report --out .\ci_report --hybrid-reasoning
```

## What changed

Agent Failure Doctor can now turn a sanitized diagnosis report into an
evidence-bound reasoning report. The report organizes claims, hypotheses,
causal-chain nodes, and root-cause graph nodes without replacing the
deterministic classifier.

## Highlights

- local-only evidence bundle generation
- deterministic `mock_reasoner` default provider
- evidence-bound claims and hypotheses
- causal-chain and root-cause graph outputs
- validator rejection for unbound, sensitive, or prohibited reasoning
- optional local provider placeholders with safe fallback
- KB, CI, console, and agent-bootstrap integration

## Validation

- `hybrid_evidence_reasoning_validation.json`: 224 local synthetic cases
- claim evidence binding: 100%
- causal-chain correctness: 97.3%
- root-cause graph correctness: 97.3%
- forbidden output: 0
- private solution leak: 0
- external API calls: 0
- model downloads: 0

## Safety

v4.0.0 does not upload raw evidence, call external model APIs, download models,
or override deterministic safety-blocked diagnoses.

Forbidden output remains blocked by validation: access-control defeat guidance,
raw secret exposure, private training details, and unbound claims are rejected.

## Known limits

- Reasoning is advisory and cannot override deterministic safety decisions.
- Optional local providers require user-managed local setup.
- Evidence-thin reports degrade to `insufficient_evidence`.

## Reproduce

```powershell
python -m tools.validation.run_hybrid_evidence_reasoning_validation
python -m tools.validation.run_p98_master_gate
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```
