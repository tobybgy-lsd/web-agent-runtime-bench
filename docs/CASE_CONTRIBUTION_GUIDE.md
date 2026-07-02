# Case Contribution Guide

You do not need to write code to contribute. Submit a sanitized failure case or
issue pack.

Checklist:

- Run `failure-doctor case intake`.
- Run `failure-doctor case publish-check`.
- Confirm `contains_real_secret`, `contains_credentials`, `contains_pii`,
  `contains_phi`, and `contains_private_solution` are all false.
- Include only sanitized summaries and synthetic or approved public-safe data.
- Do not include raw local-only folders or private training artifacts.
