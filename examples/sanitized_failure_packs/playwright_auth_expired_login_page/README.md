# Playwright Auth Expired: Login Page

This template represents a run where a page returned HTTP 200, but the browser was redirected to a login page because the authorized session expired.

Use it when:

- the network response is not a transport failure
- extraction timed out on product fields
- the final URL or DOM indicates login state
- the fix should be session refresh or login-state preflight, not selector changes

The expected diagnosis is `auth_expiry`.

