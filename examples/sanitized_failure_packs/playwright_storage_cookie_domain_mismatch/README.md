# Playwright Storage State: Cookie Domain Mismatch

Represents an authenticated Playwright run where storage state was loaded, but the session cookie domain did not match the current host.

Expected diagnosis:

- `failure_type`: `playwright_storage_state_context`
- `subtype`: `cookie_domain_mismatch`

