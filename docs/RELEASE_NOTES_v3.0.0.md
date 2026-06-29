# Agent Failure Doctor v3.0.0

v3.0.0 starts the P98 Controlled Maturity Pack. It focuses on maturity gates rather than adding another surface feature.

## What changed

- Version aligned to `3.0.0`.
- Added P98 scorecard documentation.
- Added a structured failure knowledge base with 140 local-only patterns.
- Added knowledge-base validation and search tools.
- Added crawler failure coverage matrix documentation, JSON output, and validation runner.

## Safety boundary

Anti-bot risk patterns only support detection, routing, and compliance-oriented next actions. They do not provide CAPTCHA bypass, bot evasion, fingerprint spoofing, signature cracking, IP/account pools, ban evasion, or real-platform collection guidance.

## Verification

```powershell
python -m unittest tests.test_p98_scorecard tests.test_knowledge_base_patterns tests.test_crawler_failure_coverage_matrix
python -m unittest discover -s tests -p "test_*.py"
python -m tools.knowledge_base.validate_patterns
python -m tools.validation.run_crawler_failure_coverage_matrix
```

