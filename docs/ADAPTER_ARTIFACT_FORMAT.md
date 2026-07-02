# Adapter Artifact Format

Adapter outputs use a small local JSON contract:

```json
{
  "schema_version": "adapter/v1",
  "adapter_kind": "rpa | api | mobile",
  "normalized": true,
  "local_only": true,
  "evidence": [
    {
      "evidence_id": "A001",
      "source": "adapter_artifact",
      "summary": "redacted evidence summary",
      "raw_excluded": true
    }
  ]
}
```

Adapters should emit candidates and evidence only. The core diagnosis and
safety gates remain the final authority.
