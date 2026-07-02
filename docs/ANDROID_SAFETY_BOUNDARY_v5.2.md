# Android Safety Boundary v5.2

Agent Failure Doctor v5.2.0 is a diagnosis and workflow hardening tool, not an Android bypass toolkit.

Blocked by design:

- Blocked: APK modification, re-signing, root-only behavior, hooks, or platform bypasses.
- Reading other apps' private directories, SMS, contacts, photos, credentials, tokens, cookies, or browser profiles.
- External uploads, telemetry, or real platform access in validation.
- Blocked: final action execution in default workflows.
- Absolute coordinate primary locators.

Allowed:

- Local authorized evidence review.
- Dry-run workflow compilation.
- Locator candidate recommendations with manual approval.
- Sanitized replay packs.
- Mock device matrix validation.
