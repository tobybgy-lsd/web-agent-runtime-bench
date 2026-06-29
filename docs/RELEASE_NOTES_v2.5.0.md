# Agent Failure Doctor v2.5.0

v2.5.0 adds the AI Handoff & Patch Proposal Pack. It turns existing diagnosis, fix plan, repair order, and evidence graph outputs into AI coding assistant task packs and dry-run patch proposals.

## What changed

- Package version aligned to `2.5.0`.
- Added `failure-doctor handoff <report> --target codex|claude_code|cursor|all --out <ai_handoff>`.
- Added `failure-doctor propose-patch --repo <repo> --report <report> --out <patch_plan>`.
- README and dashboard now document the lifecycle as `capture/adapt -> diagnose -> plan -> AI handoff / patch proposal -> verify -> sanitize/share`.

## Handoff output

```text
ai_handoff/
|-- ai_handoff.json
|-- ai_handoff.md
|-- codex_task.md
|-- claude_code_task.md
|-- cursor_task.md
|-- affected_files.json
|-- validation_commands.md
|-- forbidden_actions.md
|-- token_budget_report.json
`-- ai_handoff_pack.zip
```

## Patch proposal output

```text
patch_plan/
|-- patch_proposal.md
|-- proposed_changes.json
|-- affected_files.json
|-- validation_commands.md
`-- patch_risk_assessment.json
```

## Safety boundary

This release does not automatically edit source files, apply patches, run tests, open pull requests, solve challenges, bypass access controls, extract credentials, or add bot-evasion behavior.

## Validation metrics

```text
20/20 Codex task files
20/20 Claude Code task files
20/20 Cursor task files
18/20 patch proposals
0 forbidden outputs
```

## Known limits

- Patch proposal is dry-run only; it does not modify repository files.
- Generated handoff tasks still require human review before execution.

## Reproduce commands

```powershell
python -m unittest tests.test_ai_handoff_patch_proposal
python -m tools.validation.run_ai_handoff_validation
```

Expected result: 3/3 tests pass and `validation/ai_handoff_validation.json` reports 20 cases, 18 patch proposals, and 0 forbidden outputs.
