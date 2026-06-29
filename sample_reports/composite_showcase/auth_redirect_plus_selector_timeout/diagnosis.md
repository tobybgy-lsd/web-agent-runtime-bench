# auth_redirect_plus_selector_timeout

## Primary Failure
- `playwright_storage_state_context` / `login_redirect_after_authenticated_action`

## Secondary Failures
- `selector_drift` / `timeout_waiting_for_selector`

## Blocking Failure
- auth redirect/login evidence blocks downstream selector diagnosis

## Repair Order
- Restore authenticated context or session state first.
- Re-run and inspect selector symptoms only after auth succeeds.
