# Codex Fix Prompt

Please fix this Playwright authenticated-flow failure.

Diagnosis:

- category: login state expired or missing
- technical reason: playwright_storage_state_context
- subtype: login_redirect_after_authenticated_action

Requirements:

1. Check where the browser context is created.
2. Confirm the expected storage state is loaded.
3. Add a global setup or refresh step if the state is expired.
4. Keep selector changes out of scope unless the login redirect is resolved first.
5. Rerun the test with trace capture enabled.
