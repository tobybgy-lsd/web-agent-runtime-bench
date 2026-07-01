# Visual Runtime Safety Boundary

Visual runtime observability is local-only and diagnosis-only.

Allowed:

- analyze offline visual-run artifacts
- diagnose stale screenshot, DPR drift, viewport drift, coordinate drift,
  screenshot compression loss, OCR mismatch, and visual grounding failure
- compare two local runs
- generate safe next actions and manual-review guidance
- block or require sanitization when screenshots/OCR/VLM responses contain
  sensitive data

Not supported:

- CAPTCHA bypass
- anti-bot evasion
- fingerprint spoofing
- dynamic signature cracking
- Cloudflare, Akamai, DataDome, or PerimeterX bypass
- proxy, IP, or account pool guidance
- human-like mouse movement or pointer trajectory generation
- behavior mimicry for access-control defeat
- challenge solvers or private training solutions
- browser profile, credential store, cookie, or token extraction
- real-platform collection without explicit authorization

When evidence is weak, the correct output is `pure_visual_insufficient_evidence`
or manual review.
