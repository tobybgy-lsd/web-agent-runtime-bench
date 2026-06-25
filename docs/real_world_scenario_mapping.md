# Real-World Scenario Mapping

The benchmark does not collect real website data. This mapping explains which real engineering situations each synthetic task represents.

| Benchmark Task | Real Engineering Situation It Models | Boundary |
|---|---|---|
| `static_extraction` | Product/listing fields are visible in HTML and can be extracted without browser runtime repair. | Uses local synthetic fixture only. |
| `dynamic_runtime_missing` | An Agent fails because JavaScript expects `window`, `document`, `navigator`, or storage APIs. | Uses synthetic bundle and shim only. |
| `bundle_shim_repair` | A headless runtime needs a clear compatibility contract before running page logic. | No real website JavaScript. |
| `signed_mock_api` | Request verification depends on method, path, payload hash, timestamp, nonce, and synthetic browser state. | Uses `x-demo-signature`, never real signature names or algorithms. |
| `failure_diagnosis` | A failed Agent run needs a structured diagnosis and repair prompt. | Diagnoses synthetic traces only. |
| `safety_guard` | A public benchmark needs release hygiene checks before publication. | Scans for forbidden demo-code patterns. |

## Product Interpretation

This project is useful as a benchmark and debugging layer for AI web agents. A production product should live in a separate repository and focus on public or user-authorized workflows.

## Non-Goals

- Real-platform scraping
- CAPTCHA bypass
- Anti-bot evasion
- Real signature bypass
- Cookie or Authorization replay
