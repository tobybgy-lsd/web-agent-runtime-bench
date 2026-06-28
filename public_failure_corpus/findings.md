# Findings From 30 Public Cases

## Input Reality

- Most public failures are log-first or description-first, not trace-first.
- Browser-agent projects often expose task text, action history, screenshots, and environment notes rather than Playwright trace.zip.
- Screenshot-only evidence is common in reports, but v0.1 should keep it metadata-only until a safe image-understanding policy exists.

## Product Implication

Agent Failure Doctor should lead with:

1. Summary
2. Why
3. Evidence
4. Next Action
5. Fix Prompt
6. Estimated Success

Failure type is useful, but the product value is the next action a developer or operator can hand to Codex/Claude.

## Template Candidates

At least 10 cases can become local tests immediately: proxy, DNS, TLS, strict mode, target closed, execution context destroyed, navigation timeout, download not saved, CDP WebSocket disconnect, and repeated action loop.
