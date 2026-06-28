# Playwright Trace Adapter v1 Design

## Goal

Upgrade `warb adapt playwright-trace` from a filename-oriented zip scan into a local-only adapter that extracts useful failure evidence from sanitized Playwright trace archives.

This should make WebAgentRuntimeBench better at accepting user-authorized failure packs without contacting real websites, replaying requests, or storing credentials.

## Scope

In scope:

- Read a local `trace.zip` only.
- Parse common text and JSON entries such as `trace.trace`, `*.network`, `*.json`, `*.log`, `*.html`, and `*.dom`.
- Extract status code, URL, console/error messages, network event summaries, and HTML/DOM excerpts.
- Preserve the existing `failure_artifact.json` schema.
- Keep generated artifacts marked as sanitized local evidence requiring review before sharing.
- Add focused tests using synthetic trace archives.

Out of scope:

- No browser launch.
- No network replay.
- No real-platform signatures, cookies, authorization headers, or anti-bot behavior.
- No full production-grade Playwright trace viewer implementation.
- No change to Scrapy or requests adapters except shared helper cleanup if required.

## Data Flow

`warb adapt playwright-trace trace.zip --out <dir>` calls `artifact_from_playwright_trace`.

The adapter opens the zip, classifies entries by name and content, then builds one `failure_artifact.json`:

- `error.message`: concise combined error/console evidence.
- `error.status_code`: best available HTTP status.
- `observations.url`: best available final or failing URL.
- `observations.console_messages`: bounded list of console/error messages.
- `observations.network_events`: bounded list of local network summaries from trace metadata.
- `observations.html_excerpt`: bounded HTML/DOM text.
- `artifacts.trace`: original trace zip filename.

All extracted text is bounded to avoid huge artifacts.

## Parsing Rules

- Prefer structured JSON or JSONL parsing when an entry contains line-delimited Playwright trace events.
- Recognize network-like records with fields such as `url`, `status`, `statusCode`, `method`, `request`, `response`, and nested `params`.
- Recognize error-like records with fields such as `error`, `message`, `text`, `stack`, `type`, and console event hints.
- Fall back to regex status extraction and plain text snippets when JSON parsing fails.
- Keep only small summaries, not raw trace payloads.

## Error Handling

- Missing zip file raises `FileNotFoundError`, preserving current CLI behavior.
- Malformed entries are skipped with best-effort extraction rather than aborting the entire adapter.
- Binary or undecodable entries are ignored unless their filename identifies them as an artifact reference.

## Testing

Add tests before implementation:

- A synthetic trace archive containing `trace.trace` JSONL console/error and network records should produce status, URL, console messages, and network event summaries.
- A malformed or mixed trace archive should still produce a valid artifact with available evidence.
- Existing adapter tests for Scrapy and requests must continue to pass.

Verification commands:

```powershell
python -m unittest tests.test_failure_artifact_expansion
python -m unittest discover -s tests -p 'test_*.py'
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```
