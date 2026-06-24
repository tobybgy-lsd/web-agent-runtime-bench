# Safety Boundary

## Allowed (Synthetic Only)

- Synthetic JavaScript bundles (all `bundle_*.js` files)
- Local Node.js subprocess execution
- Mock API verification (x-demo-signature, SHA-256)
- Fake browser API stubs (navigator, localStorage, document, EventTarget)
- Local runtime error trace and classification
- Synthetic_browser_shim.js (IIFE providing stub browser globals)
- Synthetic example HTML, trace samples, dependency matrices
- Local smoke tests (`scripts/smoke_test.ps1`)
- User-authorized / public-safe web data automation workflows (future direction)

## Forbidden

- Real platform signatures: x-s, x-t, x-s-common
- Real website JavaScript (no dom-based scraping or eval of remote scripts)
- Real API endpoints (no http/https requests to external hosts)
- Network requests: requests.get, fetch(), axios, XMLHttpRequest
- Cookies or Authorization headers
- CAPTCHA bypass or anti-bot system evasion
- Real user-agent spoofing for production
- Database access with real credentials
- Real platform bypass logic
- Real platform examples (real websites, real API endpoints, copied website JS)
- Unauthorized data extraction from any platform
- Unauthorized data extraction from any platform
- Copying real website JavaScript or reverse-engineering proprietary signing logic

## Sensitive Token Detection

All demo code is scanned for:
- API keys (sk-* patterns)
- Real platform header names
- Network request patterns
- Sensitive field names (Cookie, Authorization)

Scan script: `scripts/local_safety_scan.ps1`
