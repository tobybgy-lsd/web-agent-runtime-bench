# Attribution

## LearnSpider Challenge Pool

The original LearnSpider challenge pool (315 baseline challenges, levels 46–360) is based on publicly available web scraping textbook materials and serves as an experimental foundation. This project does **not** claim original authorship of the challenge pool.

## What This Project Does NOT Contain

This showcase repository does **not** include:
- The full 315-challenge database or its answers
- Hidden oracle values or expected answers
- Ground truth data
- API keys or credentials
- Challenge factory code
- Solver registry code
- Real platform data or real website logic

## Showcase Contributions

The following extensions represent the original showcase contributions of this project:

### Phase 5.1: AI-Agent Web Extraction Evaluation Harness
- Visible observation pipeline (agent only sees pre-collected data)
- Anti-leakage design (no hidden oracle, no /api/check-answer, no /admin)
- Preimage candidate generator with multi-rule scoring
- Response shape router (flat/nested/config/mixed JSON classification)
- Oracle guard, failure replay, and capability dashboard

### Phase 5.2: Synthetic Dynamic Web Runtime Benchmark
- Runtime error classifier (rule-based pattern matching)
- Synthetic browser shim (IIFE stubs for window, document, navigator, EventTarget, localStorage)
- 5 synthetic obfuscated bundles with runtime contract checks
- Locally-signed mock API (WARBDemoV1/V2, x-demo-signature, SHA-256)
- 6-case signed API dependency matrix benchmark
- Dependency tracer (path, payload_hash, timestamp, nonce, userAgent, salt, meta token, event token)
- Negative tampered-payload verification

## Future Product Direction

Any future product development will focus on AI-powered web data automation for **public and user-authorized workflows only**. No unauthorized scraping, no anti-bot bypass, no proprietary signature reverse-engineering.

## References

- LearnSpider: public web scraping textbook materials (experimental foundation)
- All demo code: synthetic/local-only Node.js subprocess execution
