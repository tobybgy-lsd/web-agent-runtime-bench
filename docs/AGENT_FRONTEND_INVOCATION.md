# Agent Frontend Invocation Pack

Agent Failure Doctor is the local failure diagnosis backend. AI coding tools are frontends that call it, read the report, explain the evidence, and optionally repair code.

Generate invocation instructions for a project:

```powershell
failure-doctor agent-bootstrap --target all --project .
```

Generate a single target:

```powershell
failure-doctor agent-bootstrap --target codex --project .
failure-doctor agent-bootstrap --target cursor --project .
failure-doctor agent-bootstrap --target claude_code --project .
failure-doctor agent-bootstrap --target vscode_copilot --project .
failure-doctor agent-bootstrap --target antigravity --project .
failure-doctor agent-bootstrap --target opencode --project .
failure-doctor agent-bootstrap --target qoder --project .
failure-doctor agent-bootstrap --target trae --project .
failure-doctor agent-bootstrap --target workbuddy --project .
failure-doctor agent-bootstrap --target openclaw --project .
failure-doctor agent-bootstrap --target hermes --project .
failure-doctor agent-bootstrap --target generic_agent --project .
```

## Output

```text
.failure-doctor/
|-- AGENT_ENTRYPOINT.md
`-- agents/
    |-- agent_invocation_manifest.json
    |-- codex/
    |   |-- instructions.md
    |   |-- diagnose_project.md
    |   |-- repair_workflow.md
    |   |-- allowed_commands.md
    |   `-- forbidden_actions.md
    |-- cursor/
    |-- claude_code/
    |-- vscode_copilot/
    |-- antigravity/
    |-- opencode/
    |-- qoder/
    |-- trae/
    |-- workbuddy/
    |-- openclaw/
    |-- hermes/
    `-- generic_agent/
```

Each target gets the same safe backend contract:

```powershell
failure-doctor collect --project . --preset auto --out .\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize
```

## Responsibility Split

Agent Failure Doctor handles:

- local evidence collection
- diagnosis
- fix planning
- AI handoff
- sanitization
- verification workflow guidance

The AI frontend handles:

- calling `failure-doctor`
- reading the generated report
- explaining the result to the user
- proposing code edits only when evidence is sufficient
- running project verification commands

## Safety Boundary

The generated pack is local-only and project-scoped.

Forbidden:

- scanning outside the project
- browser profile access
- credential store access
- external upload of raw evidence
- CAPTCHA bypass
- bot evasion
- fingerprint spoofing
- signature cracking
- IP/account pool guidance
- credential extraction
- unauthorized real-platform collection

