# WebAgentRuntimeBench: Dynamic Web Runtime Benchmark for AI Agents

WebAgentRuntimeBench is a **public-safe research prototype** and benchmark harness for AI-agent web extraction and synthetic dynamic web runtime evaluation.

WebAgentRuntimeBench 是一个面向 AI Agent 的动态 Web 运行时评测框架，覆盖网页抽取评测、防作弊设计、failure replay、browser runtime shim、synthetic signature challenge。

## What This Is

- A **synthetic-only** dynamic web runtime benchmark
- An **evaluation harness** for AI-agent web data extraction (Phase 5.1)
- A **runtime shim framework** for browser APIs in headless Node.js (Phase 5.2)
- A **local mock** signed API challenge generator
- A **safety-first** research prototype with explicit anti-leakage boundaries

## What This Is NOT

- Not a production crawler
- Not a real-platform scraper
- Not a signature bypass tool
- Not a CAPTCHA bypass tool
- Not a tool for evading anti-bot systems
- Not a real website data collector

## Current Status

| Phase | Status | Key Result |
|-------|--------|-----------|
| 5.1-A3 | **Frozen** | 315/315 baseline PASS, evaluation harness frozen, PASS=0 on agent solving |
| 5.2-A0 | **PASS** | Synthetic dynamic runtime MVP: shim repair, classifier, mock API |
| 5.2-A1 | **PASS** | Runtime shim variants: 3/5 classified, full shim success |
| 5.2-A2 | **PASS** | Synthetic bundle variants: 5/5 classified, 5/5 full shim, 5/5 mock API accepted |

### Phase 5.2 Detailed Results

| Variant | Classified Failures | Full Shim Success | Mock API Accepted | External Network |
|---------|:---:|:---:|:---:|:---:|
| A0 (runtime demo) | 1/1 | ✅ | ✅ | 0 |
| A1 (shim variants) | 3/5 | ✅ | ✅ | 0 |
| A2 (bundle variants) | 5/5 | 5/5 | 5/5 | 0 |

## Quickstart

**Requirements:** Python 3.10+, Node.js 18+

No network required. No API keys needed. No cookies or auth tokens.

```powershell
cd demo\phase5_2_runtime

# A0: Synthetic runtime demo
python run_synthetic_runtime_demo.py --out-dir ..\..\sample_run\a0 --node node

# A2: Bundle variant cases
python run_bundle_variant_cases.py --out-dir ..\..\sample_run\a2 --node node
```

Expected: all cases PASS with external_network=0.

## Safety Boundary

✅ **Allowed (synthetic only):**
- Synthetic JavaScript bundles
- Local mock API verification (x-demo-signature)
- Fake navigator, localStorage stubs
- Runtime error trace and classification
- Local `subprocess.run(["node", ...])` only

❌ **Forbidden:**
- Real platform signatures (x-s, x-t, x-s-common)
- Real website JavaScript
- Real API endpoints
- Network requests (http/https/fetch/axios)
- Cookies or Authorization headers
- CAPTCHA bypass or anti-bot evasion
- Database access with real credentials

## Architecture

```
Phase 5.1: AI-Agent Web Extraction Evaluation Harness
├── 315 baseline challenges (public canonical)
├── Visible observation pipeline
├── Preimage candidate generator
├── Response shape router
└── Evaluation harness (frozen)

Phase 5.2: Synthetic Dynamic Web Runtime Benchmark
├── Runtime error classifier (rule-based, no model)
├── Synthetic browser shim (window, document, navigator...)
├── Synthetic obfuscated bundles (runtime contract checks)
├── Locally-signed mock API (x-demo-signature, SHA-256)
├── Dependency tracer (path, payload_hash, UA, salt, algorithm)
└── Failure replay & capability dashboard
```

## Roadmap

- **A3**: Synthetic signed API benchmark (multi-dependency variants)
- **A4**: Public-safe showcase hardening
- **A5**: Package for distribution
- **GitHub release**: After safety audit only

## Attribution

The original LearnSpider challenge pool is based on publicly available web scraping textbook materials and serves as an experimental foundation. The extensions — evaluation harness, runtime benchmark framework, failure replay system, capability dashboard, shim design, signed API mock, and synthetic bundle variants — represent the showcase contributions.

## License

MIT (pending final review)
