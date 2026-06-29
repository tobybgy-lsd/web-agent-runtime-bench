# Agent Failure Doctor v2.4.1

v2.4.1 is a P95 alignment release. It does not add a new product direction; it collects the existing validation work into a single public, machine-readable gate and fills the missing P95 quantity tracks.

## Highlights

- Package version aligned to `2.4.1`.
- README and dashboard now point to `Agent Failure Doctor v2.4.1 P95 Alignment & Missing Tracks Pack`.
- Added `validation/p95_core_triage_gate.json`.
- Added `tools.validation.run_p95_core_triage_gate`.
- Added 100-case Cross-Framework P95 validation.
- Added 40-case Training Challenge P95 validation.
- Added 100-case Playwright Trace Doctor P95 validation.
- Added 3 composite showcase reports under `sample_reports/composite_showcase/`.

## P95 Gate

```text
overall_status: pass
playwright_trace_doctor: pass
cross_framework_adapters: pass
training_challenge_sedimentation: pass
composite_diagnosis: pass
safety_boundary: pass
```

## Safety

This release remains local-first and diagnostic-only. It does not add CAPTCHA bypass, bot evasion, fingerprint spoofing, signature cracking, credential extraction, or private challenge solution logic.

## Reproduce

```powershell
python -m tools.validation.run_playwright_trace_p95_validation
python -m tools.validation.run_cross_framework_p95_validation
python -m tools.validation.run_training_challenge_validation
python -m tools.validation.run_composite_diagnosis_p95_strict_validation
python -m tools.validation.run_p95_core_triage_gate
python -m unittest discover -s tests -p "test_*.py"
```
