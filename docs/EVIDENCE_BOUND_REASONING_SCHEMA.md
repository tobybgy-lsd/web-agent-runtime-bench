# Evidence-Bound Reasoning Schema

## Evidence Bundle

```json
{
  "schema_version": "reasoning_evidence_bundle/v1",
  "sanitized_only": true,
  "raw_content_excluded": true,
  "evidence_items": [
    {
      "evidence_id": "E001",
      "source": "diagnosis",
      "summary": "technical_category: network_http_error; subtype: proxy_connection_failed",
      "severity": "medium",
      "confidence": 0.86,
      "raw_excluded": true
    }
  ]
}
```

## Reasoning Report

Each claim must cite known evidence:

```json
{
  "claim_id": "claim_001",
  "claim_type": "root_cause",
  "text": "network/proxy evidence likely caused downstream automation failure",
  "supporting_evidence_ids": ["E001"],
  "is_evidence_bound": true
}
```

Validation rejects unknown IDs, missing IDs, sensitive output, and prohibited
guidance.
