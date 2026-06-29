# Real User Feedback Loop

v3.2.0 is the stable technical baseline. The next phase is external validation:
real people running the tool on real, sanitized failure evidence.

## First Target

Collect 5 real sanitized failure cases.

These cases should come from users or external projects, not from author-created
templates.

## Intake Path

Users should open:

```text
.github/ISSUE_TEMPLATE/external_failure_case.yml
```

They can provide any safe subset of:

- `error.log`
- `trace.zip` metadata or sanitized trace archive
- `console.txt`
- `network.json`
- screenshot metadata
- `user_description.txt`

## Triage Rules

For each accepted case:

1. Confirm the submitter has permission to share the material.
2. Confirm credentials, cookies, tokens, authorization headers, private URLs,
   personal data, and customer data are removed.
3. Assign an id such as `EXT-YYYY-NNNN`.
4. Run the current released version first-run before rule changes.
5. Record expected category, actual category, confidence, next action quality,
   and whether the report was useful.
6. If the case exposes a real gap, create a regression case after the first-run
   result is recorded.

Rule: do not count synthetic examples, local templates, or author-generated
examples as external-user cases.

## Success Criteria

The first external-feedback milestone is:

- 5 real sanitized failure cases
- 5 generated reports
- at least 3 reports judged useful by the submitter or maintainer
- 0 secrets in accepted public artifacts
- 0 forbidden outputs

## What To Ask For

Ask for failure samples, not stars.

Suggested request:

```text
If you have a sanitized failed Playwright, Selenium, Scrapy, RPA, or AI agent
run, please open an External Failure Case issue. Logs, trace metadata, network
summaries, screenshots metadata, and a short description are enough.
```

## What Not To Accept

Reject or ask for redaction when a case contains:

- passwords
- cookies
- tokens
- authorization headers
- API keys
- private URLs
- customer data
- personal data
- instructions for CAPTCHA bypass, bot evasion, fingerprint spoofing, dynamic
  signature cracking, credential extraction, or unauthorized collection
