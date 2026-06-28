# Playwright Selector Drift: Product Card

This template represents a common Playwright failure where a product card was redesigned and the old price selector no longer exists.

Use it when:

- the page loaded successfully
- authentication is valid
- no rate-limit or challenge page is present
- Playwright timed out on a stale locator
- the saved DOM contains nearby candidate fields that can replace the old selector

The expected diagnosis is `selector_drift`.

