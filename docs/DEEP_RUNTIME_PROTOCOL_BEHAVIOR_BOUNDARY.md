# Deep Runtime, Protocol, and Behavioral Evidence Boundary

Agent Failure Doctor v3.2.8 can ingest sanitized, user-supplied evidence about
deep browser runtime, protocol-stack, and behavioral telemetry failures. These
signals are diagnosis inputs only. They are not active probes, bypass recipes,
or crawler execution features.

## Public-safe evidence

The public package may classify these sanitized subtypes:

- `webgl_virtual_renderer_detected`
- `webrtc_private_ip_leak_detected`
- `automation_global_scope_leak_detected`
- `runtime_sandbox_leak_detected`
- `native_function_integrity_mismatch`
- `debugger_timing_anomaly`
- `http2_settings_fingerprint_mismatch`
- `ja4_h2_fingerprint_mismatch`
- `js_vmp_integrity_check_failed`
- `numeric_semantics_mismatch`
- `pointer_trajectory_entropy_anomaly`
- `mathematical_trajectory_detected`

Accepted public evidence should be summaries such as:

- WebGL renderer/vendor family, not raw collection scripts.
- WebRTC candidate category summaries, not private network details.
- Browser global-scope key summaries, not cleanup code.
- Native reflection and debugger timing summaries, not anti-debugging steps.
- ALPN, HTTP version, HTTP/2 SETTINGS, and protocol-stack summaries.
- Client-VM integrity and numeric-semantics summaries, not bytecode or formulas.
- Pointer movement entropy buckets, not generated movement paths.

## Safe output

Reports should say:

- Treat the evidence as a runtime, protocol, or behavioral risk boundary.
- Do not misclassify it as selector, storage, or proxy failure.
- Collect sanitized evidence before changing automation code.
- Prefer official APIs, SDKs, compliant exports, or approved test hooks.
- Stop automation when authorization or platform terms are unclear.

## Private-only material

The public package must not include:

- local challenge servers, solvers, or flags
- browser stealth implementation details
- WebGL, WebRTC, Canvas, native-reflection, or global-scope alteration recipes
- protocol impersonation values or transport-stack alignment instructions
- VMP bytecode interpreters, formulas, constants, or reconstruction logic
- pointer trajectory generation, timing mimicry, or behavioral bypass steps
- CAPTCHA solving, bot evasion, credential extraction, or account/IP rotation

## Why this boundary exists

The goal is to help authorized developers understand why an AI browser
automation, RPA, or Playwright run failed. The tool should route users toward
compliant fixes and better evidence, not toward access-control defeat.
