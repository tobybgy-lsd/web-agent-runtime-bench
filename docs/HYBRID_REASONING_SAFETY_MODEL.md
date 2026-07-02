# Hybrid Reasoning Safety Model

Hybrid reasoning is allowed only over sanitized local evidence.

The validator checks:

- every claim cites a known `evidence_id`
- every hypothesis includes a verification strategy
- confidence values are in range
- no raw secret markers are present
- no private local training details are present
- no prohibited access-control guidance is present
- no external API call is required
- no model download is required

When validation fails, the report is marked rejected and the caller must fall
back to deterministic diagnosis.

Safe use:

- ask for missing evidence when confidence is low
- explain why the primary diagnosis is stronger than alternatives
- preserve manual review when safety or authorization is unclear
- keep all raw material local
