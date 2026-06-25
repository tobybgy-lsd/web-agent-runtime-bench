# Roadmap

## Phase 5.2-A3: Synthetic Signed API Benchmark ✅ DONE
- 6 signed API cases (path_payload / timestamp_nonce / user_agent_salt / document_meta_token / event_token / full_matrix)
- 6/6 verified, 6/6 negative rejected, dependency range 3–9
- All synthetic/local mock only. No real platform signatures.
- Synced to showcase via A4.

## Phase 5.2-A4: Showcase Sync + Private Push ✅ DONE
- A3 code synced to D:\WebAgentRuntimeBench-GitHub
- README/docs/demo/sample_reports updated
- Pushed to GitHub private repo (tobybgy-lsd/web-agent-runtime-bench)
- Public release remains CONDITIONAL — requires manual review

## Developer Toolkit Polish v1 ✅ DONE
- Cookbook with 5 practical recipes
- Runtime diagnosis patterns, signed API dependency patterns, failure replay patterns
- Developer toolkit positioning document
- Examples: static product list, dynamic runtime missing, signed API dependency matrix
- `scripts/smoke_test.ps1` for one-command validation
- All synthetic/local-only, no real platform content

## Benchmark Credibility Layer v1 ✅ DONE
- Standard six-task benchmark suite
- Deterministic scoring protocol with per-dimension weights
- Comparison baselines for static parsing, shim repair, signed mock API checks, diagnosis, and safety guard
- Third-party reproducibility guide
- GitHub Actions benchmark workflow with report artifact upload
- Real-world scenario mapping without real-platform collection

## Future

- **Synthetic benchmark expansion**: More task fixtures, harder bundle variants, richer negative cases
- **External reproducibility runs**: Ask third parties to run the standard suite and attach CI/report artifacts
- **Product MVP (optional)**: Separate repository for public and user-authorized web data automation
