# Public Failure Corpus

This corpus is a product-discovery asset for Agent Failure Doctor. It collects public, sanitized failure patterns from Playwright, browser-use, Stack Overflow-style Q&A, and agent framework issue trackers.

The cases are not training data and do not copy private traces, cookies, tokens, screenshots, or full issue bodies. Each case keeps only a source URL, short symptom summary, raw-error style excerpt, evidence, likely category, and whether it can become a local regression/template.

Use this corpus to decide which input types and next-action outputs matter most before adding more failure subtypes.
