# Playwright Shadow DOM: Test ID Missing Strategy

Represents a locator failure where a useful test id existed inside shadow DOM, but the test did not use a shadow-aware strategy.

Expected diagnosis:

- `failure_type`: `playwright_shadow_dom_locator`
- `subtype`: `testid_inside_shadow_dom_missing_strategy`

