# Regulated Industry Workflow Pack

`failure-doctor regulated-eval` runs local-only synthetic mock suites for
finance, government, healthcare, and cross-industry automation workflows.

```powershell
failure-doctor regulated-eval --suite finance --out .\regulated_report
failure-doctor regulated-eval --suite government --out .\regulated_report
failure-doctor regulated-eval --suite healthcare --out .\regulated_report
failure-doctor regulated-eval --suite all --out .\regulated_report
```

The pack checks evidence quality and shareability signals such as synthetic
PII/PHI leakage, audit-chain gaps, attachment workflow failures, OCR/document
parse mismatch, report export field loss, approval-state mismatch, and unsafe
AI handoff content.

It does not connect to real finance, government, healthcare, patient, citizen,
bank, or customer systems. It is not legal, medical, financial, or regulatory
compliance advice.

Outputs:

- `regulated_eval_result.json`
- `regulated_eval_result.md`
- `regulated_cases.json`

Safety boundary:

- local-only
- synthetic/mock only
- no real platform access
- no real regulated data
- no form submission to real regulated systems
- no bypass, evasion, spoofing, cracking, or credential extraction guidance
