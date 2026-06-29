# Real Data Sources

v0.8 separates source credibility from validation fixtures.

## Ledger

`validation/source_ledger_real_failures.json`

Current counts:

| Source Type | Count |
|---|---:|
| `real_public_issue` | 50 |
| `official_doc_pattern` | 10 |
| `public_inspired_sanitized` | 71 |
| Total | 131 |

## Definitions

`real_public_issue`
: A traceable public issue URL. The ledger stores a short sanitized symptom and expected diagnosis, not a copied full issue body.

`official_doc_pattern`
: An official documentation URL used to define expected tool behavior or evidence boundaries.

`public_inspired_sanitized`
: A sanitized validation record inspired by recurring public failure patterns. It must not pretend to be a real issue URL.

## Rules

- Do not use fake GitHub issue URLs.
- Do not label sanitized records as real public issues.
- Preserve enough raw error excerpt to make the category auditable.
- Store source type, source status, category, symptom, expected diagnosis, and reproduction notes.
- Never store secrets, cookies, tokens, authorization headers, private URLs, personal data, or customer data.

## Why This Matters

The classifier is useful only if its validation language is honest. Template fixtures are good for regression; real public issue URLs are good for credibility; native Playwright traces are good for adapter semantics. They answer different questions and must remain separate.
