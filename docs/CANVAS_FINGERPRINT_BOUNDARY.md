# Canvas Fingerprint Boundary

Agent Failure Doctor may diagnose sanitized Canvas fingerprint evidence when a
user provides local logs or an offline `browser_runtime_report.json`.

## Public-safe signals

The public package may classify:

- `canvas_fingerprint_collision`
- `browser_canvas_fingerprint_risk`

Accepted evidence should stay high level and sanitized:

- repeated Canvas hash counts across sessions
- total session counts
- HTTP rejection status
- browser/runtime metadata summaries
- source label such as `sanitized-authorized-test`

## Public-safe next actions

The tool should recommend:

- treat Canvas fingerprint evidence as an access-policy or runtime-consistency
  signal, not a selector/storage/proxy bug
- collect sanitized Canvas hash/session-count evidence before changing code
- confirm whether an authorized API, official SDK, compliant export,
  documented test hook, or platform-approved integration exists
- stop automation when authorization or platform terms are unclear

## Do not publish

Do not publish local challenge solvers, flags, rendering-hook details, Canvas
output alteration recipes, fingerprint spoofing instructions, anti-bot evasion
logic, private mock server details, or real-platform bypass procedures.

This boundary keeps local training useful while keeping the public project a
diagnosis-only developer tool.
