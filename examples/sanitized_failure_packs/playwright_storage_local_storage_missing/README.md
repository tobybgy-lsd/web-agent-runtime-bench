# Playwright Storage State: Local Storage Missing

Represents a run where cookies existed, but the app required a localStorage/sessionStorage key that was absent from the saved state.

Expected diagnosis:

- `failure_type`: `playwright_storage_state_context`
- `subtype`: `local_storage_missing`

