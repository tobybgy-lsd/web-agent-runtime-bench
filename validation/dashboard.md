# Validation Dashboard

| Track | Samples | Reasonable Classification | Actionable Next Action | Severe Misclassification | Insufficient Evidence | Tests |
|---|---:|---:|---:|---:|---:|---:|
| Template/synthetic validation | 150 | 97.3% | 94.7% | 4 | 21 | 170 |
| Public-inspired independent validation | 50 | 78% | 90% | 4 | 7 | n/a |
| Real Playwright trace semantic fixtures | 3 | n/a | n/a | n/a | n/a | 197 |
| v0.6.0 website-change / anti-bot routing | 50 | 100% | 100% | 0 | 0 | 197 |

## Notes

- Template/synthetic validation records are sanitized fixtures, not full real-world failure packages.
- Public-inspired independent validation is tracked as a separate stricter track and must not be averaged with template fixture metrics.
- Real Playwright trace semantic fixtures use native trace records such as `Network.requestWillBeSent`, `Network.responseReceived`, `Page.frameNavigated`, and Playwright action records without custom classifier fields.
- Reasonable Classification means the diagnosis matches the expected broad category, or safely downgrades to insufficient evidence.
- Actionable Next Action means the report gives a concrete next debugging step or a safe compliance-oriented route.
- Severe Misclassification means the diagnosis points to the wrong broad layer.
- Insufficient Evidence means the tool avoids guessing and asks for more material.
- Tests are the current local unit-test count at the time of the dashboard update.
- The 150-record template track uses a broad "reasonable classification" criterion. The 50-record public-inspired independent validation uses a narrower correctness criterion, so it is the more conservative estimate for production-like precision.

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
