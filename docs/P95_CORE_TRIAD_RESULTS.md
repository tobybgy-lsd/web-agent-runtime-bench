# P95 Core Triad Results

This project separates controllable maturity from ecosystem maturity. Stars,
external issues, external pull requests, and package downloads are not counted in
this local validation score.

## Composite Diagnosis P95 Strict Gate

- Cases: 160 local-only composite/adversarial fixtures
- Primary failure correct: 160/160
- Repair order correct: 160/160
- Evidence graph valid: 160/160
- Forbidden output: 0

## Current Interpretation

Composite diagnosis is now validated as a first-class failure lifecycle layer:
the tool can preserve old single-failure fields while exposing primary,
secondary, blocking, downstream, evidence graph, and repair order fields for
advanced diagnosis and fix planning.
