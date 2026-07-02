# Local Reasoner Setup

The default v4.0 path needs no model:

```powershell
failure-doctor reason --input .\report --out .\report\hybrid_reasoning --provider mock_reasoner
```

Optional local providers are intentionally conservative:

```powershell
failure-doctor reason --input .\report --out .\reasoning --provider ollama_local --model llama3.1
failure-doctor reason --input .\report --out .\reasoning --provider llama_cpp_local --model-path .\models\local.gguf
```

Agent Failure Doctor does not download models and does not call external model
APIs for these commands. If the local runtime is missing, it returns a safe
fallback and keeps the deterministic report.
