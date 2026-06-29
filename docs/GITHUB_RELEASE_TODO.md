# GitHub Release TODO

The repository has release-note drafts prepared for the public alignment line. Publish releases only from the intended tags/commits; do not attach historical release names to the wrong commit.

## Prepared release notes

| Version | Notes file | Suggested title | Status |
|---|---|---|---|
| v2.4.1 | `docs/RELEASE_NOTES_v2.4.1.md` | Agent Failure Doctor v2.4.1 - P95 Alignment & Missing Tracks | pending publication as latest stable |
| v2.5.0 | `docs/RELEASE_NOTES_v2.5.0.md` | Agent Failure Doctor v2.5.0 - AI Handoff & Patch Proposal | ready for manual publication |
| v2.6.0 | `docs/RELEASE_NOTES_v2.6.0.md` | Agent Failure Doctor v2.6.0 - Batch Diagnosis / Fleet Mode | ready for manual publication |
| v3.0.0 | `docs/RELEASE_NOTES_v3.0.0.md` | Agent Failure Doctor v3.0.0 - P98 Controlled Maturity Skeleton | ready for manual publication |
| v3.0.1 | `docs/RELEASE_NOTES_v3.0.1.md` | Agent Failure Doctor v3.0.1 - Public Alignment & P98 Track Separation | not yet; development track only |

## Suggested manual steps

```powershell
gh release create v2.4.1 --title "Agent Failure Doctor v2.4.1 - P95 Alignment & Missing Tracks" --notes-file docs/RELEASE_NOTES_v2.4.1.md
```

For historical releases, first confirm that each tag points to the intended commit:

```powershell
git tag --list "v2.4.1" "v2.5.0" "v2.6.0" "v3.0.0" "v3.0.1"
git show --stat v2.4.1
```

If a historical tag does not exist, create it only after confirming the correct commit boundary in the changelog.

Keep `v3.0.1` out of GitHub Releases until the P98 development track has a final master gate. Its release notes remain a development-track record, not the packaged stable release.

## Safety note

Release text must keep the same boundary as the project: local-first diagnosis, repair planning, verification, and sanitized sharing only. Do not market the project as CAPTCHA bypass, bot evasion, credential extraction, protected-signature cracking, or a real-platform crawler.
