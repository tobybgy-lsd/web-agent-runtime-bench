# Codex Execution Report: v2.4.1 Release & README First-Screen Polish

Date: 2026-06-29

## Scope

This pass is public-entry polish only. It does not add diagnosis features, crawler behavior, or P98 completion claims.

## Release Status

GitHub Release `v2.4.1` is already published as the latest stable release:

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v2.4.1

Current public structure:

- Stable line: `v2.4.1`
- P95 gate: passed
- P98 track: `v3.0.x`, in progress

## README First Screen

The README first screen was compressed to emphasize:

- one-line positioning
- current stable milestone
- P98 development-track status
- supported input/output
- core commands
- three quickstart commands
- validation and safety links

Longer details such as advanced handoff, patch proposal, batch/fleet mode, P98 gates, composite diagnosis, integrations, and full validation metrics remain in later sections.

## Verification

Commands run locally:

```powershell
python -m unittest tests.test_open_source_entry tests.test_public_release_cleanup tests.test_release_alignment_pack tests.test_release_trust_pack tests.test_version_alignment
python -m unittest discover -s tests -p "test_*.py"
python -m tools.validation.run_p95_core_triage_gate
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
powershell -ExecutionPolicy Bypass -File scripts\local_safety_scan.ps1
```

Results:

- README/public-entry tests: 27 passed
- Full unittest suite: 319 passed
- P95 core triage gate: pass
- Smoke test: pass
- Local safety scan: pass

## Safety Boundary

No CAPTCHA bypass, bot evasion, fingerprint spoofing, protected-signature cracking, credential extraction, private challenge solution logic, or real-platform collection workflow was added.
