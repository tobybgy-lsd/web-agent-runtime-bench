# Contributing

You do not need to write code.

The most useful contribution is a sanitized failure case.

## Submit a Failure Case

Please include:

- tool: Playwright / browser-use / Scrapy / requests / Codex / RPA / other
- input type: trace.zip / error.log / console.txt / network.json / screenshot / description
- what failed
- expected behavior
- actual behavior
- sanitized error excerpt
- whether this can become a public test case

## Contribute a Failure Case Without Code

Open an External failure case issue and attach only sanitized material:

- `error.log`
- `trace.zip`
- `console.txt`
- `network.json`
- screenshot metadata
- `user_description.txt`

If you allow public reuse, maintainers may assign a stable id such as `EXT-2026-0001`, run the current released version before changing rules, and record the first-run result in `validation/external_validation_dashboard.md`.

Accepted public cases may later become regression tests. Templates and author-generated examples are not counted as external cases.

## Do Not Include

- credentials
- cookies
- tokens
- authorization headers
- private URLs
- private data
- personal data
- customer data

## Run Tests

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Windows smoke test:

```powershell
scripts\smoke_test.ps1
scripts\local_safety_scan.ps1
```

## Pull Request Checklist

- Add or update tests for behavior changes.
- Run unit tests before opening a pull request.
- Run the safety scan for changes touching docs, reports, prompts, or diagnosis output.
- Do not include sensitive data in fixtures, screenshots, traces, logs, or examples.

If Discussions are enabled, please submit non-sensitive failure cases under Failure Cases.

See `docs/external_validation_protocol.md` and `docs/REAL_TRACE_CONTRIBUTION_GUIDE.md` for the full external validation flow.
