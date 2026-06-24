# Public Release Checklist

This checklist must be completed by a human reviewer before changing GitHub repo visibility from PRIVATE to PUBLIC.

## Pre-Release Checklist

| # | Item | Status |
|:--:|------|:---:|
| 1 | GitHub visibility is currently PRIVATE | ✅ |
| 2 | README has no overclaim (no "crawler", "scraper", "bypass", "production") | ✅ |
| 3 | Attribution document is clear and linked from README | ✅ |
| 4 | LICENSE file is present (MIT) | ✅ |
| 5 | Sample reports contain no sensitive data (no answers, no API keys, no real URLs) | ✅ |
| 6 | Demo code does not access external network | ✅ |
| 7 | Demo code contains no real platform logic (no x-s/x-t, no Cookie/Authorization) | ✅ |
| 8 | `scripts/local_safety_scan.ps1` passes cleanly | ✅ |
| 9 | A0 demo (runtime) passes | ✅ |
| 10 | A2 demo (bundle variants) passes | ✅ |
| 11 | A3 demo (signed API benchmark) passes | ✅ |
| 12 | `sk-` pattern scan is clean (only docs + scan script) | ✅ |
| 13 | Overclaim phrases not present in any text | ✅ |

## Human Decision Required

| # | Decision |
|:--:|----------|
| 14 | **Change repo visibility to PUBLIC** ← requires explicit human action |
| 15 | Do NOT link to resume/LinkedIn unless a separate resume-focused audit is done |

## Post-Public Rules

- Continue enforcing safety boundary: no real platform signatures, no real scraping logic
- Any new code must pass `scripts/local_safety_scan.ps1` before merge
- Attribution and LICENSE must be kept up to date
