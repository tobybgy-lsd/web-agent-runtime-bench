# Hybrid Evidence Reasoning

Agent Failure Doctor v4.0 adds a local hybrid reasoning layer on top of the
deterministic diagnosis engine.

The goal is not to replace the classifier. The goal is to turn sanitized report
artifacts into an evidence bundle, then generate:

- evidence-bound claims
- competing hypotheses
- a causal chain
- a root-cause graph
- validation records for every claim

## Commands

```powershell
failure-doctor reason --input .\report --out .\report\hybrid_reasoning
failure-doctor root-cause --input .\report --out .\root_cause_report
failure-doctor causal-chain --input .\report --out .\causal_chain_report
failure-doctor diagnose .\failed_run --hybrid-reasoning --out .\report
failure-doctor diagnose .\failed_run --kb .\.failure-doctor-kb --hybrid-reasoning --out .\report
failure-doctor ci diagnose --project .\report --out .\ci_report --hybrid-reasoning
```

## Output

The reasoning report writes:

- `reasoning_evidence_bundle.json`
- `hybrid_reasoning_report.json`
- `hybrid_reasoning_summary.md`
- `causal_chain_report.json`
- `root_cause_graph.json`
- `competing_hypotheses.json`
- `reasoning_validation.json`
- `reasoning_audit.json`

## Safety Model

Every claim must cite at least one `evidence_id`. If a claim is unbound,
contains sensitive material, or uses prohibited guidance, validation rejects it
and the tool falls back to deterministic rules.

The default provider is `mock_reasoner`, which is deterministic, local, and
does not call external APIs.
