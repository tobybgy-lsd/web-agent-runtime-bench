# Causal Chain And Root-Cause Graph

Hybrid reasoning writes two machine-readable structures:

- `causal_chain_report.json`
- `root_cause_graph.json`

The causal chain is chronological. The root-cause graph separates:

- primary root cause
- secondary contributors
- downstream symptoms
- rejected causes
- verification plan

This helps keep a report from over-focusing on downstream symptoms such as
"button not found" when stronger evidence points to a prior network, auth,
visual, OCR, data-quality, or website-change failure.

Reasoning remains advisory. The deterministic diagnosis and safety gates remain
authoritative.
