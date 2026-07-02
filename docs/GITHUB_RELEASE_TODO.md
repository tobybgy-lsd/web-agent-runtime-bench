# GitHub Release TODO

The repository has release-note drafts prepared for the public alignment line. Publish releases only from the intended tags/commits; do not attach historical release names to the wrong commit.

## Prepared release notes

| Version | Notes file | Suggested title | Status |
|---|---|---|---|
| v2.4.1 | `docs/RELEASE_NOTES_v2.4.1.md` | Agent Failure Doctor v2.4.1 - P95 Alignment & Missing Tracks | published as latest stable |
| v2.5.0 | `docs/RELEASE_NOTES_v2.5.0.md` | Agent Failure Doctor v2.5.0 - AI Handoff & Patch Proposal | ready for manual publication |
| v2.6.0 | `docs/RELEASE_NOTES_v2.6.0.md` | Agent Failure Doctor v2.6.0 - Batch Diagnosis / Fleet Mode | ready for manual publication |
| v3.0.0 | `docs/RELEASE_NOTES_v3.0.0.md` | Agent Failure Doctor v3.0.0 - P98 Controlled Maturity Skeleton | ready for manual publication |
| v3.0.1 | `docs/RELEASE_NOTES_v3.0.1.md` | Agent Failure Doctor v3.0.1 - Public Alignment & P98 Track Separation | not yet; development track only |
| v3.1.0 | `docs/RELEASE_NOTES_v3.1.0.md` | Agent Failure Doctor v3.1.0 - P98 Master Gate Completion Pack | published as latest stable |
| v3.2.0 | `docs/RELEASE_NOTES_v3.2.0.md` | Agent Failure Doctor v3.2.0 - Auto Collector & One-Click Diagnosis Pack | published |
| v3.2.2 | `docs/RELEASE_NOTES_v3.2.2.md` | Agent Failure Doctor v3.2.2 - Spiderbuf-Inspired Safe Diagnostics Patch | published |
| v3.2.3 | `docs/RELEASE_NOTES_v3.2.3.md` | Agent Failure Doctor v3.2.3 - TLS/ALPN Safe Diagnostics Patch | published |
| v3.2.4 | `docs/RELEASE_NOTES_v3.2.4.md` | Agent Failure Doctor v3.2.4 - Offline Probe Evidence Boundary Patch | published |
| v3.2.5 | `docs/RELEASE_NOTES_v3.2.5.md` | Agent Failure Doctor v3.2.5 - Behavioral and Client Hints Evidence Patch | published |
| v3.2.6 | `docs/RELEASE_NOTES_v3.2.6.md` | Agent Failure Doctor v3.2.6 - JavaScript Integrity Evidence Patch | published |
| v3.2.7 | `docs/RELEASE_NOTES_v3.2.7.md` | Agent Failure Doctor v3.2.7 - Canvas Fingerprint Evidence Patch | published |
| v3.2.8 | `docs/RELEASE_NOTES_v3.2.8.md` | Agent Failure Doctor v3.2.8 - Deep Runtime Evidence Patch | published |
| v3.2.9 | `docs/RELEASE_NOTES_v3.2.9.md` | Agent Failure Doctor v3.2.9 - Visual and Data Quality Diagnostics Patch | published |
| v3.2.10 | `docs/RELEASE_NOTES_v3.2.10.md` | Agent Failure Doctor v3.2.10 - Data Engineering Closed-Loop Triage Patch | published |
| v3.3.0 | `docs/RELEASE_NOTES_v3.3.0.md` | Agent Failure Doctor v3.3.0 - Safety & Compliance Evaluation Pack | published |
| v3.5.0 | `docs/RELEASE_NOTES_v3.5.0.md` | Agent Failure Doctor v3.5.0 - OCR & Document Evidence Adapter Pack | ready for publication after gates pass |
| v3.6.0 | `docs/RELEASE_NOTES_v3.6.0.md` | Agent Failure Doctor v3.6.0 - Regulated Industry & Pure Visual Agent Full-Chain Evaluation Pack | published |
| v3.7.0 | `docs/RELEASE_NOTES_v3.7.0.md` | Agent Failure Doctor v3.7.0 - Local Web Console Pack | published |
| v3.8.0 | `docs/RELEASE_NOTES_v3.8.0.md` | Agent Failure Doctor v3.8.0 - CI/CD Integration Pack | published |
| v3.9.0 | `docs/RELEASE_NOTES_v3.9.0.md` | Agent Failure Doctor v3.9.0 - Local Failure Knowledge Base Pack | published |
| v4.0.0 | `docs/RELEASE_NOTES_v4.0.0.md` | Agent Failure Doctor v4.0.0 - Hybrid Evidence Reasoning Pack | published |
| v4.1.0 | `docs/RELEASE_NOTES_v4.1.0.md` | Agent Failure Doctor v4.1.0 - Enterprise Governance & Role-Based Console Pack | published |
| v4.2.0 | `docs/RELEASE_NOTES_v4.2.0.md` | Agent Failure Doctor v4.2.0 - Plugin SDK & Adapter Ecosystem Pack | ready for publication after gates pass |

## Published release

`v4.2.0` is the next release candidate for the latest stable GitHub Release.

After publication, the release URL should be:

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.2.10

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.3.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.5.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.6.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.7.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.8.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.9.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v4.0.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v4.1.0

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v4.2.0

`v3.2.0` is the previous stable GitHub Release:

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.2.0

PyPI is published:

https://pypi.org/project/agent-failure-doctor/

Install command:

```powershell
python -m pip install agent-failure-doctor
```

`v3.1.0` remains the previous stable GitHub Release:

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v3.1.0

`v2.4.1` remains the previous stable P95 GitHub Release:

https://github.com/tobybgy-lsd/web-agent-runtime-bench/releases/tag/v2.4.1

For historical releases, first confirm that each tag points to the intended commit:

```powershell
git tag --list "v2.4.1" "v2.5.0" "v2.6.0" "v3.0.0" "v3.0.1"
git show --stat v2.4.1
```

If a historical tag does not exist, create it only after confirming the correct commit boundary in the changelog.

Keep `v3.0.1` as a development-track record. `v3.1.0` was published only after the P98 master gate, unit tests, smoke test, safety scan, and GitHub Actions were green. `v3.2.0` was published after the auto collector validation, P98 master gate, smoke test, safety scan, GitHub Actions, and PyPI release were green.

## Safety note

Release text must keep the same boundary as the project: local-first diagnosis, repair planning, verification, and sanitized sharing only. Do not market the project as CAPTCHA bypass, bot evasion, credential extraction, protected-signature cracking, or a real-platform crawler.
