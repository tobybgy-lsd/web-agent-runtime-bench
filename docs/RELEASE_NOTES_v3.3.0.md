# Agent Failure Doctor v3.3.0 - Safety & Compliance Evaluation Pack

v3.3.0 upgrades Agent Failure Doctor from a local failure diagnosis and AI
handoff backend into a local-only safety and compliance evaluation tool for
automation failure artifacts.

## Install

```powershell
python -m pip install agent-failure-doctor==3.3.0
failure-doctor --help
failure-doctor safety-evaluate --help
```

PyPI: https://pypi.org/project/agent-failure-doctor/

## What changed

- Added `failure-doctor safety-evaluate`.
- Added `collect --safety-evaluate`.
- Added local safety reports for collector scope, secrets, shareability, AI
  handoff, patch proposals, DOM risk, permission boundary, data exfiltration,
  offline cloud-browser artifacts, and regulated workflow mocks.
- Added `safety_compliance_evaluation` to the P98 master gate.
- Added package private-content scanning for wheel/sdist artifacts.

## Safety boundary

This release is local-only, evidence-only, no upload, and no active probe.
It does not provide CAPTCHA bypass, anti-bot evasion, fingerprint spoofing,
dynamic signature cracking, protected signature reconstruction, proxy/account
pool guidance, browser stealth recipes, behavioral mimicry, VMP reconstruction,
challenge solvers, credential extraction, browser profile reading, credential
store reading, or private challenge pass logic.

For anti-bot, challenge, fingerprint, signature, runtime, and cloud-browser
artifact evidence, outputs are limited to risk detection, manual review,
official API / authorization guidance, sanitization, shareability decisions,
and stop-if-unauthorized recommendations.

## Validation

- Safety compliance validation: 175 local-only synthetic/mock cases.
- P98 master gate includes the new safety compliance pillar.
- Forbidden output count: 0.
- Private solution leak count: 0.
- Real platform access count: 0.
- Active probe count: 0.
- Browser profile access count: 0.
- Credential store access count: 0.

## Reproduce

```powershell
python -m unittest discover -s tests -p "test_*.py"
python -m tools.validation.run_safety_compliance_validation
python -m tools.validation.run_p98_master_gate
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

## Known limits

- Safety evaluation is a local evidence review, not legal advice.
- Cloud-browser artifact review is offline-only and does not call provider APIs.
- Regulated workflow checks use local mock artifacts only and do not connect to
  real finance, government, healthcare, ERP, or ecommerce systems.
- Anti-bot, challenge, fingerprint, signature, and runtime evidence remains
  diagnosis-only and compliance-oriented.
