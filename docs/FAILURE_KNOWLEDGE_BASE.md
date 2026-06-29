# Failure Knowledge Base

The failure knowledge base is a local-only set of public-safe diagnostic patterns used to connect evidence, failure classes, fix-plan templates, and verification strategies.

Patterns live under `knowledge_base/` and are validated by:

```powershell
python -m tools.knowledge_base.validate_patterns
```

The P98 validator writes `validation/knowledge_base_p98_validation.json`.
