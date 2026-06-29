# Validation Dashboard

| Version | Samples | Reasonable Classification | Actionable Next Action | Severe Misclassification | Insufficient Evidence | Tests |
|---|---:|---:|---:|---:|---:|---:|
| v0.6.0 | 150 + 50 v0.6 routing records | 98.0% | 96.0% | 4 | 21 | 197 |
| v0.4.0 | 150 | 97.3% | 94.7% | 4 | 21 | 170 |
| v0.4.0 strict independent evaluation | 50 | 78% | 90% | 4 | 7 | n/a |

## Notes

- Samples are public-inspired sanitized validation records, not full real-world failure packages.
- Reasonable Classification means the diagnosis matches the expected broad category, or safely downgrades to insufficient evidence.
- Actionable Next Action means the report gives a concrete next debugging step or a safe compliance-oriented route.
- Severe Misclassification means the diagnosis points to the wrong broad layer.
- Insufficient Evidence means the tool avoids guessing and asks for more material.
- Tests are the current local unit-test count at the time of the dashboard update.
- The 150-record row uses a broad "reasonable classification" criterion. The 50-record strict independent evaluation uses a narrower correctness criterion, so it is the more conservative estimate for production-like precision.

## v0.6.0 Website Change / Anti-Bot Addendum

The v0.6.0 addendum is tracked separately in `validation/website_antibot_validation_50.json`.

| Metric | Result |
|---|---:|
| Website Change records | 25 |
| Anti-Bot Risk records | 25 |
| Reasonable classifications | 50/50 |
| Safe next actions | 50/50 |
| Forbidden outputs | 0 |
| Severe misclassifications | 0 |

Anti-bot risk output is limited to identification, routing, and compliant next actions. It does not provide CAPTCHA bypass, bot evasion, credential extraction, network rotation, account rotation, or private signature bypass guidance.
