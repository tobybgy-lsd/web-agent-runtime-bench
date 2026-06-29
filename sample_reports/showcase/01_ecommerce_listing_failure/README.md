# Showcase 01: Ecommerce Listing Failure

Local-only applied scenario sample showing a listing automation failure.

## Input Summary

- Input type: applied scenario failed run
- Domain: mock ecommerce listing automation
- Evidence: error log, user description, before/after rerun folder

## Detected Failure

- User-facing category: browser environment mismatch
- Technical category: toolchain_environment
- Subtype: missing_browser_dependency

## Suggested Next Action

Run the fix plan, install or pin the missing browser dependency, then verify the before/after run with `failure-doctor verify`.
