# Android Production Runbook

Operators should start with local-only dry-run workflows:

1. Check farm status.
2. Check device health.
3. Lease one device per task.
4. Run Appium planning only unless a local operator starts Appium.
5. Bind sanitized task data.
6. Schedule dry-run tasks.
7. Review failed tasks and replay packs.
8. Use mutation guard before any submit-like or mutation-like flow.

Offline devices, Appium session failures, permission dialogs, missing locators,
image picker failures, disabled buttons, final submit blocks, and mutation blocks
are normal triage outcomes. Final submit blocked and business mutation blocked are
design behaviors.

