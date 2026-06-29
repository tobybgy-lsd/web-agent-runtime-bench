# Agent Failure Doctor v3.1.0 - P98 Master Gate Completion Pack

v3.1.0 promotes the controlled-maturity track from P98 development to a machine-checked P98 master gate. The gate is local-first and excludes ecosystem maturity signals such as stars, forks, third-party integrations, PyPI downloads, and long-term community adoption.

## What changed

- Added P98 validation runners for Playwright trace, cross-framework adapters, training challenge sedimentation, composite/counterfactual diagnosis, AI handoff and patch proposal, batch/fleet diagnosis, and sanitize/share.
- Expanded the failure knowledge base to 200+ public-safe local synthetic patterns.
- Expanded the crawler failure coverage matrix to 24+ categories and 300+ mapped local synthetic cases.
- Added `tools.validation.run_p98_master_gate` to aggregate all P98 pillar results.
- Promoted `validation/p98_master_gate.json` to a final gate only when every pillar passes.

## P98 pillar metrics

```text
Knowledge Base P98: 210 patterns, 0 forbidden outputs, 0 private solution leaks
Crawler Matrix P98: 26 categories, 312 mapped cases, 0 forbidden outputs
Playwright Trace P98: 220 local synthetic native-trace fixture records, 218/220 reasonable, 212/220 exact, 0 forbidden outputs
Cross-framework P98: 240 local synthetic cases, 238/240 reasonable, 240/240 actionable, 0 forbidden outputs
Training Challenge P98: 200 local synthetic challenge-inspired cases, 178/180 diagnosis threshold met, 0 private solution leaks
Composite + Counterfactual P98: 280 local synthetic cases, 276/280 primary correct, 69/70 counterfactual pairs correct
AI Handoff P98: 100 reports, 100/100 assistant task packs, proposal-only patch plans, 0 forbidden outputs
Batch / Fleet P98: 30 batch sets, 200-run local batch covered, 0 forbidden outputs
Sanitize / Share P98: 120 local synthetic cases, 100% secrets redacted, 0 raw secrets in output
```

## Safety boundary

This release remains diagnostic-only. It does not provide CAPTCHA bypass, bot evasion, fingerprint spoofing, protected-signature cracking, credential extraction, private challenge solution logic, IP/account pool guidance, or real-platform collection workflows.

## Known limits

- P98 is controlled project maturity, not ecosystem maturity.
- P98 does not mean universal business logic understanding.
- P98 does not mean automatic repair of every source-code failure.
- P98 does not include external adoption or long-term third-party production usage.

## Reproduce commands

```powershell
python -m pip install -e .
python -m unittest discover -s tests -p "test_*.py"
python -m tools.knowledge_base.validate_patterns
python -m tools.validation.run_crawler_failure_coverage_matrix
python -m tools.validation.run_playwright_trace_p98_validation
python -m tools.validation.run_cross_framework_p98_validation
python -m tools.validation.run_training_challenge_p98_validation
python -m tools.validation.run_composite_counterfactual_p98_validation
python -m tools.validation.run_ai_handoff_p98_validation
python -m tools.validation.run_batch_diagnosis_p98_validation
python -m tools.validation.run_sanitize_share_p98_validation
python -m tools.validation.run_p98_master_gate
python -m tools.validation.run_p95_core_triage_gate
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```
