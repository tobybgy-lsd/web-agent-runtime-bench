# Sanitized Failure Pack Templates

These templates show the shape of realistic, public-safe failure packs that users can submit or adapt.

They are intentionally local and sanitized:

- no cookies, tokens, passwords, authorization headers, or real signatures
- no live endpoints or network replay requirements
- placeholder domains only
- short evidence files instead of full private dumps

Each directory contains:

- `failure_artifact.json` for `warb validate` and `warb diagnose`
- a short `README.md` explaining the failure
- sanitized evidence files referenced by the artifact

Use these as starting points when preparing a real failure pack for maintainers.

