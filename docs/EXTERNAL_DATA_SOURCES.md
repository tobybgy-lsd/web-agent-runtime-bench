# External Data Sources

This pack contains 62 external public reference seeds for Agent Failure Doctor v0.9.

These sources are not submitted to this repository by external users. They are public references and official documentation patterns used to start an external-source validation ledger.

## Source Types

| Source type | Count |
|---|---:|
| real_public_issue | 43 |
| real_public_qa | 14 |
| official_doc_pattern | 5 |

Validation use:

- `external_public_reference`: public issue or Q&A used as a traceable source seed
- `official_doc_pattern`: official documentation used as behavior boundary or correct-use reference

Do not copy long issue content into this repository. Keep only `source_url`, title, category, expected diagnosis, and a short sanitized summary.

## Held-Out 20

| Metric | Value |
|---|---:|
| Total held-out cases | 20 |
| Reasonable category match | 20/20 |
| Exact category match | 20/20 |
| Exact subtype match | N/A |
| Actionable next_action | 20/20 |
| Severe misclassification | 0 |
| Insufficient evidence | 0 |
| Forbidden output count | 0 |

Safety rule: Anti-bot risk samples are identification and compliant routing only. They must not generate challenge-bypass, bot-evasion, fingerprint-spoofing, dynamic-signature-cracking, IP-pool, account-pool, or CAPTCHA-automation guidance.

## Files

- `validation/source_ledger_external_seed_v0_9.json`
- `validation/source_ledger_external_seed_v0_9.csv`
- `validation/external_public_reference_ledger.json`
- `validation/external_heldout_20_cases.json`
- `validation/external_heldout_20.json`

Reproduce:

```powershell
python -m tools.validation.run_external_public_reference_validation
```
