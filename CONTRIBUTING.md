# Contributing

You do not need to write code.

The most useful contribution is to submit a sanitized failure case that helps
Agent Failure Doctor learn where real AI browser automation, crawler, RPA, or
Playwright runs fail.

## Submit a sanitized failure case

Open a Failure case issue and include:

- What failed?
- What tool? Playwright / browser-use / Codex / RPA / other
- Input type: log / trace / network / screenshot / description
- Expected result
- Actual result
- Sanitized log
- Can this become a public test case?

Do not include passwords, API keys, cookies, tokens, authorization headers, or private screenshots.

Also remove:

- personal data
- account IDs
- customer names
- private URLs
- proprietary request payloads
- full trace files that contain private DOM or network data

## What Makes a Good Case

A useful case has enough evidence to explain the failure without exposing the
real account, platform, or user data.

Good:

```text
page.goto: net::ERR_PROXY_CONNECTION_FAILED while opening https://example.test
Tool: Playwright
Expected: open dashboard
Actual: navigation failed before page load
Can this become a public test case? yes
```

Avoid:

```text
Here is my full trace.zip with cookies and screenshots.
```

## Safety Boundary

This project does not help bypass CAPTCHA, bot defenses, credential checks, or
platform restrictions. Anti-bot risk reports should only identify risk and
suggest compliant next actions such as using an official API, confirming
authorization, reducing request volume, contacting the platform, or stopping
unauthorized collection.
