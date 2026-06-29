# Fix Plan

## Root Cause

The authenticated browser context did not preserve the expected login state.

## Recommended Change

- Confirm `browser.newContext({ storageState })` is used for this test.
- Regenerate the local auth state when expired.
- Verify that the configured base URL matches the stored cookie origin.
- Add trace capture on repeated failure.

## Verification

Rerun the authenticated action and confirm no login redirect occurs before the target click.
