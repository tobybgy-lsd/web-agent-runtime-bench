# Validation Dashboard

| Version | Samples | Reasonable Classification | Actionable Next Action | Severe Misclassification | Insufficient Evidence | Tests |
|---|---:|---:|---:|---:|---:|---:|
| v0.6.0 | 200 | 88%+ target | 90%+ target | ≤5 target | calibrated | 200+ target |
| v0.4.0 | 150 | 97.3% | 94.7% | 4 | 21 | 170 |

## Notes

- Samples: public-inspired sanitized validation records, not full real-world failure packages.
- Reasonable Classification: the diagnosis matches the expected broad category, or safely downgrades to insufficient evidence.
- Actionable Next Action: the report gives a concrete next debugging step.
- Severe Misclassification: cases where the diagnosis points to the wrong broad layer.
- Insufficient Evidence: cases where the tool avoids guessing and asks for more material.
- Tests: current unit test count at the time of this dashboard update.
- v0.6.0 adds 50 public-inspired sanitized Website Change / Anti-Bot Risk corpus records and keeps anti-bot output limited to identification, routing, and compliant next actions.
