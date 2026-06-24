# Failure Diagnosis CLI v1 Report

**Task**: Failure Diagnosis CLI v1
**Date**: 2026-06-24
**Repo**: [tobybgy-lsd/web-agent-runtime-bench](https://github.com/tobybgy-lsd/web-agent-runtime-bench)
**Visibility**: PUBLIC

## New Files

| File | Purpose |
|------|---------|
| `tools/diagnostics/diagnose_failure.py` | Rule-based failure diagnosis CLI |
| `tools/diagnostics/__init__.py` | Package init |
| `examples/failure_diagnosis/` (6 files) | Synthetic failure trace samples |
| `scripts/diagnosis_smoke_test.ps1` | Diagnosis CLI smoke test |

## Updated Files

| File | Changes |
|------|---------|
| `scripts/smoke_test.ps1` | Added diagnosis smoke test step |
| README, cookbook, roadmap, safety_boundary, release_checklist | TBD in commit |

## CLI Features

| Feature | Value |
|---------|-------|
| Supported inputs | `--input-dir`, `--run-summary`, `--trace`, `--failure-replay` |
| Supported outputs | `diagnosis.json`, `diagnosis.md`, `codex_repair_prompt.md` |
| Supported failure types | 10 (missing_window/document/navigator/localStorage/EventTarget, bundle_not_registered, signed_api_verification, negative_not_rejected, unknown, pass) |
| Target agent | `codex` (Codex / WorkBuddy) |
| Rule-based | Yes (no LLM calls) |
| Synthetic only | Yes |

## Verification

| Check | Result |
|-------|:---:|
| py_compile | ✅ PASS |
| diagnosis_smoke_test.ps1 | ✅ PASS |
| smoke_test.ps1 (full) | ✅ PASS |
| local_safety_scan.ps1 | ✅ PASS |
| sk- check (code dirs) | ✅ Clean |
| Sensitive scan (code dirs) | ✅ Clean |
| D:\LearnSpider changed | NO |
| Demo logic changed | NO |
| Real platform logic added | NO |
| UI added | NO |
| Product MVP added | NO |

## Conclusion

**Failure Diagnosis CLI v1: PASS**

## Next Suggestion

Optional: Production Sample Extractor v0, additional failure patterns, CI workflow integration.
