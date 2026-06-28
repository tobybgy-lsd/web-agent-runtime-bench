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

## Do Not Include

- credentials
- cookies
- tokens
- authorization headers
- private URLs
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
