# Scrapy Rate Limit: Soft Block

This template represents a crawler response that returned HTTP 429 and a generic "try again later" body.

Use it when:

- the response status or body shows throttling
- downstream extraction received an empty product list
- changing selectors would hide the real access/rate-limit problem
- the fix should be authorized backoff, lower concurrency, or scheduling changes

The expected diagnosis is `rate_limit_or_soft_block`.

