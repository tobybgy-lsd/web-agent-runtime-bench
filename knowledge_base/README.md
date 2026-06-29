# Failure Knowledge Base

The knowledge base stores structured, local-only diagnostic patterns for Agent Failure Doctor.

Patterns are JSON files grouped by use:

- `failure_patterns/`
- `fix_patterns/`
- `evidence_patterns/`
- `framework_patterns/`
- `domain_patterns/`
- `regression_patterns/`

Each pattern describes evidence, negative evidence, fix intent, verification expectations, and safety boundaries. Anti-bot risk patterns are detection and routing assets only; they must not include bypass instructions.

Use:

```powershell
python -m tools.knowledge_base.validate_patterns
python -m tools.knowledge_base.search_patterns --query selector_drift
```

