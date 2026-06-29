# Fix Plan

## Root Cause

The failed-run evidence may contain private details unless explicitly sanitized and reviewed.

## Recommended Change

- Run `failure-doctor sanitize`.
- Inspect the redaction report.
- Confirm no private screenshots, raw traces, credentials, or customer data remain.
- Share only the sanitized pack after review.

## Verification

Check that `safe_to_share=false` is present and that the pack contains only sanitized files.
