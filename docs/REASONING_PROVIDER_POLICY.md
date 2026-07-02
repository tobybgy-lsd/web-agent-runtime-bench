# Reasoning Provider Policy

Hybrid reasoning is local-first.

Supported providers:

- `mock_reasoner`: deterministic local provider, enabled by default.
- `ollama_local`: optional local-only provider; unavailable unless the user has
  already installed and configured Ollama.
- `llama_cpp_local`: optional local-only provider; unavailable unless a local
  model path is supplied.
- `imported_reasoning`: imports a user-provided JSON reasoning result and then
  validates it against the evidence bundle.

Provider rules:

- no external API calls by default
- no model download
- no raw evidence upload
- no browser profile access
- no credential-store access
- deterministic diagnosis remains the source of truth
- high-confidence safety-blocked decisions cannot be overridden by reasoning

If an optional provider is unavailable, the tool returns a safe fallback instead
of attempting network setup.
