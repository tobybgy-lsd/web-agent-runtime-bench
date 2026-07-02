# Console Security Model

Agent Failure Doctor v3.7 exposes a local web console for report inspection.
The model is intentionally narrow.

## Local Binding

The default bind address is `127.0.0.1`. Non-loopback hosts are rejected unless
the user passes `--allow-lan`.

## Workspace Scope

The console creates a workspace, defaulting to `.failure-doctor-console`.
Workspace reads and writes are scoped under that directory. Path traversal and
sensitive local paths are blocked.

Sensitive examples include:

- `raw_local_only_do_not_share`
- browser profile folders
- credential stores
- cookie stores
- private keys and token-like paths

## POST Token

All POST routes require `X-Console-Token`. The token is generated locally and
stored in the console workspace manifest.

## No External Assets

The HTML, CSS, and JavaScript are bundled with the Python package. The console
does not use CDN assets and does not call external services.

## Shareability

The console can preview shareable report content, but raw local evidence is
hidden by default. Use `failure-doctor sanitize` before sending material to
another person or AI coding assistant.
