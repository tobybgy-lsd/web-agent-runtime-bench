# External Case Template

This is a non-external sample template. It is not a real user submission and must not be counted in external validation metrics.

Copy this shape into a private folder when preparing a sanitized case:

```text
my_external_case/
|-- error.log
|-- console.txt
|-- network.json
|-- user_description.txt
`-- screenshot_metadata.json
```

Run locally:

```powershell
failure-doctor diagnose .\my_external_case --out .\report
```

Before sharing, remove credentials, cookies, tokens, authorization headers, private data, private URLs, customer data, and personal information.

