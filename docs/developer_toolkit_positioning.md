# Developer Toolkit Positioning

## Current Position

WebAgentRuntimeBench is positioned as a **developer-facing benchmark and debugging toolkit** for AI web agents, NOT a production crawler, scraper, or UI product.

### What It Is

- **Benchmark** — reproducible AI-agent web extraction and runtime evaluation
- **Debugging Toolkit** — runtime diagnosis, classifier, failure replay
- **Cookbook** — practical recipes for common web agent debugging scenarios
- **Public-Safe Synthetic Runtime Lab** — local-only mock cases, no real platforms

### What It Is NOT

- ❌ Production crawler
- ❌ Real-platform scraper
- ❌ Anti-bot bypass toolkit
- ❌ CAPTCHA bypass toolkit
- ❌ UI SaaS product
- ❌ Real-platform data collection service

### What Developers Can Learn

1. Why JS bundles fail outside browser runtimes
2. How to classify missing runtime objects
3. How to validate synthetic signed API behavior
4. How to build positive/negative verification cases
5. How to replay extraction and runtime failures
6. How to design safer extraction benchmarks

### Relationship to Future Product

- This repository is the **technical benchmark/toolkit layer**
- Any product MVP should be in a **separate repository**
- Any product MVP must focus on **public and user-authorized workflows**
- No real-platform scraping or bypass should ever appear in this repo

### Safety Constraints

- All demos: synthetic/local-only
- No external network
- No real platform signatures (x-s, x-t, x-s-common)
- No Cookie or Authorization headers
- No unauthorized data extraction
- No anti-bot evasion
