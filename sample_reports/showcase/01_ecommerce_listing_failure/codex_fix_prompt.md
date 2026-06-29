# Codex Fix Prompt

Please fix this local automation failure.

Diagnosis:

- category: browser environment mismatch
- technical reason: toolchain_environment
- subtype: missing_browser_dependency

Requirements:

1. Add a browser-runtime preflight check.
2. Keep the listing workflow logic unchanged.
3. Save stdout, stderr, and environment metadata when the command fails.
4. Add a regression test for missing browser executable handling.
5. Run the affected test and `failure-doctor verify` after the fix.
