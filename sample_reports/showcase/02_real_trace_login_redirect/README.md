# Showcase 02: Real Trace Login Redirect

Native Playwright trace fixture sample showing a login redirect before an authenticated action.

## Input Summary

- Input type: Playwright `trace.zip` fixture
- Evidence: trace metadata, navigation events, network redirect evidence
- Raw trace content: not included in this showcase

## Detected Failure

- User-facing category: login state expired or missing
- Technical category: playwright_storage_state_context
- Subtype: login_redirect_after_authenticated_action

## Suggested Next Action

Regenerate or load the correct storage state, confirm base URL and origin, and rerun the authenticated action.
