# Collector Security Model

Agent Failure Doctor collection is designed for authorized local debugging.

## Guarantees

- Local-only: no upload or remote API call.
- Project-scoped: only the user-selected project folder is scanned.
- Copy-only: source files are not modified.
- Sanitized output: share `sanitized_failure_pack/`, not raw local evidence.

## Explicitly Skipped

- `.git`
- `node_modules`
- `.venv`, `venv`, `env`
- `__pycache__`
- browser profile folders and cookie stores
- SSH private keys and credential stores

## Not Supported

This collector is not a CAPTCHA bypass tool, bot evasion tool, credential extractor, or unauthorized scraping tool. Anti-bot and access-control signals are routed to safe next actions only.
