from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PACK_VERSION = "3.6.0"

AGENT_TARGETS = (
    "codex",
    "cursor",
    "claude_code",
    "vscode_copilot",
    "antigravity",
    "opencode",
    "qoder",
    "trae",
    "workbuddy",
    "openclaw",
    "hermes",
    "generic_agent",
)


@dataclass(frozen=True)
class AgentTargetProfile:
    display_name: str
    mode: str
    role: str


TARGET_PROFILES: dict[str, AgentTargetProfile] = {
    "codex": AgentTargetProfile("Codex", "first-class coding agent", "run commands, inspect reports, propose and verify patches"),
    "cursor": AgentTargetProfile("Cursor", "first-class coding agent", "run terminal workflows and use the report as patch context"),
    "claude_code": AgentTargetProfile("Claude Code", "first-class terminal agent", "run the local diagnosis workflow and produce conservative edits"),
    "vscode_copilot": AgentTargetProfile("VS Code / Copilot Agent", "first-class IDE agent", "use workspace instructions and terminal commands"),
    "antigravity": AgentTargetProfile("Google Antigravity", "workflow target", "call the local backend and summarize evidence to the user"),
    "opencode": AgentTargetProfile("OpenCode", "first-class open source coding agent", "invoke the same diagnose-plan-verify workflow"),
    "qoder": AgentTargetProfile("Qoder", "IDE workflow target", "turn diagnosis output into an IDE task plan"),
    "trae": AgentTargetProfile("Trae", "IDE workflow target", "route automation failures through the local backend first"),
    "workbuddy": AgentTargetProfile("WorkBuddy", "RPA/workbench workflow target", "collect local evidence and explain next actions in plain language"),
    "openclaw": AgentTargetProfile("OpenClaw", "local assistant runtime target", "use strict sandbox boundaries before tool calls"),
    "hermes": AgentTargetProfile("Hermes", "memory-safe workflow target", "record lessons only after verified local evidence"),
    "generic_agent": AgentTargetProfile("Generic Agent", "portable agent workflow", "give any AI frontend a safe backend invocation contract"),
}


def bootstrap_agent_frontend(project: Path, target: str = "generic_agent") -> dict[str, Any]:
    project = project.resolve()
    if not project.exists() or not project.is_dir():
        raise FileNotFoundError(f"project not found: {project}")
    targets = _select_targets(target)
    root = project / ".failure-doctor"
    agents_root = root / "agents"
    agents_root.mkdir(parents=True, exist_ok=True)

    (root / "AGENT_ENTRYPOINT.md").write_text(_render_entrypoint(targets), encoding="utf-8")
    for item in targets:
        profile = TARGET_PROFILES[item]
        target_dir = agents_root / item
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "instructions.md").write_text(_render_instructions(item, profile), encoding="utf-8")
        (target_dir / "diagnose_project.md").write_text(_render_diagnose_project(item, profile), encoding="utf-8")
        (target_dir / "repair_workflow.md").write_text(_render_repair_workflow(item, profile), encoding="utf-8")
        (target_dir / "allowed_commands.md").write_text(_render_allowed_commands(), encoding="utf-8")
        (target_dir / "forbidden_actions.md").write_text(_render_forbidden_actions(), encoding="utf-8")
        (target_dir / "safety_policy.md").write_text(_render_safety_policy(), encoding="utf-8")
        (target_dir / "safety_evaluation_workflow.md").write_text(_render_safety_evaluation_workflow(), encoding="utf-8")
        (target_dir / "regulated_workflow.md").write_text(_render_regulated_workflow(), encoding="utf-8")
        (target_dir / "visual_runtime_workflow.md").write_text(_render_visual_runtime_workflow(), encoding="utf-8")
        (target_dir / "ocr_evidence_workflow.md").write_text(_render_ocr_evidence_workflow(), encoding="utf-8")
        (target_dir / "full_chain_evaluation_workflow.md").write_text(_render_full_chain_evaluation_workflow(), encoding="utf-8")

    manifest: dict[str, Any] = {
        "schema_version": "agent_invocation_pack/v1",
        "pack_version": PACK_VERSION,
        "project": str(project),
        "targets": targets,
        "target_count": len(targets),
        "entrypoint": str(root / "AGENT_ENTRYPOINT.md"),
        "agents_root": str(agents_root),
        "safety": {
            "local_only": True,
            "project_scoped_only": True,
            "no_external_upload": True,
            "no_browser_profile_access": True,
            "no_credential_store_access": True,
            "no_captcha_bypass": True,
            "no_bot_evasion": True,
        },
        "recommended_command": "failure-doctor collect --project . --preset auto --auto-diagnose --auto-handoff --auto-sanitize --safety-evaluate",
        "regulated_eval_command": "failure-doctor regulated-eval --suite all --out .\\regulated_report",
        "visual_runtime_command": "failure-doctor visual-runtime diagnose --input .\\visual_run --out .\\visual_report --no-dom --safety-evaluate",
        "ocr_evidence_command": "failure-doctor ocr-evidence extract --input .\\failure_evidence --out .\\ocr_report --provider mock_ocr --safety-evaluate",
        "full_chain_eval_command": "failure-doctor full-chain-eval --input .\\failed_run --out .\\full_chain_report --include-safety --include-ocr --include-visual --include-regulated",
    }
    (agents_root / "agent_invocation_manifest.json").write_text(_json(manifest), encoding="utf-8")
    return manifest


def _select_targets(target: str) -> list[str]:
    if target == "all":
        return list(AGENT_TARGETS)
    if target not in AGENT_TARGETS:
        raise ValueError(f"unsupported target: {target}")
    return [target]


def _render_entrypoint(targets: list[str]) -> str:
    names = ", ".join(TARGET_PROFILES[target].display_name for target in targets)
    return f"""# Agent Failure Doctor Entrypoint

Targets generated for: {names}

When this project fails, do not guess from logs manually.

Run:

```powershell
failure-doctor collect --project . --preset auto --auto-diagnose --auto-handoff --auto-sanitize --safety-evaluate
```

Then read:

- `.failure-doctor` launcher guidance in this file
- `failure_doctor_auto_report/open_this_first.md`
- `failure_doctor_auto_report/report/diagnosis.md`
- `failure_doctor_auto_report/ai_handoff/codex_task.md`

Then propose a patch only if evidence is sufficient.

Never:

- scan outside project
- read browser profiles
- read credential stores
- upload raw evidence externally
- bypass CAPTCHA
- bypass anti-bot
- spoof fingerprints
- crack signatures
- use IP/account pools
"""


def _render_instructions(target: str, profile: AgentTargetProfile) -> str:
    return f"""# {profile.display_name} Instructions

You are using Agent Failure Doctor as the local failure diagnosis backend.

Target id: `{target}`
Target mode: {profile.mode}
Frontend role: {profile.role}

Default behavior:

1. Stay inside the authorized project folder.
2. Run the collector command from `diagnose_project.md`.
3. Read `open_this_first.md`, `report/diagnosis.md`, and the AI handoff files.
4. Explain the root cause, evidence, risk, and next action in plain language.
5. Edit code only after evidence is sufficient.
6. Verify the fix with the project test command or a minimal reproduction.

Keep Playwright trace analysis, framework log normalization, report generation, sanitize, handoff, fix planning, and verification inside `failure-doctor`.
"""


def _render_diagnose_project(target: str, profile: AgentTargetProfile) -> str:
    return f"""# Diagnose Project with {profile.display_name}

From the project root, run:

```powershell
failure-doctor collect --project . --preset auto --out .\\failure_doctor_auto_report --auto-diagnose --auto-handoff --auto-sanitize --safety-evaluate
```

Read in this order:

1. `.\\failure_doctor_auto_report\\open_this_first.md`
2. `.\\failure_doctor_auto_report\\collection_manifest.json`
3. `.\\failure_doctor_auto_report\\report\\diagnosis.md`
4. `.\\failure_doctor_auto_report\\fix_plan\\fix_plan.md`
5. `.\\failure_doctor_auto_report\\ai_handoff\\codex_task.md`

If evidence is insufficient, ask for the missing trace, log, network summary, screenshot, or user description instead of guessing.
"""


def _render_repair_workflow(target: str, profile: AgentTargetProfile) -> str:
    return f"""# Repair Workflow for {profile.display_name}

Use this workflow:

1. Collect evidence with `failure-doctor collect`.
2. Identify the primary failure layer and subtype from `diagnosis.json`.
3. Read the confidence reason and missing evidence list.
4. If the report has a fix plan, make the smallest scoped change.
5. Run the affected test or reproduction.
6. Run `failure-doctor verify` when before/after evidence is available.
7. Run `failure-doctor sanitize` before sharing any pack.

Patch rules:

- Prefer local, conservative fixes.
- Keep unrelated business logic unchanged.
- Add or update regression tests for the diagnosed failure.
- If anti-bot risk is diagnosed, provide compliance next actions only.
"""


def _render_allowed_commands() -> str:
    return """# Allowed Commands

Allowed within the authorized project only:

```powershell
failure-doctor collect --project . --preset auto --auto-diagnose --auto-handoff --auto-sanitize --safety-evaluate
failure-doctor diagnose .\\failure_doctor_auto_report --out .\\failure_doctor_manual_report
failure-doctor plan .\\failure_doctor_auto_report\\report --out .\\failure_doctor_auto_report\\fix_plan
failure-doctor verify --before .\\before --after .\\after --out .\\verification
failure-doctor sanitize .\\failure_doctor_auto_report --out .\\shareable_failure_pack
python -m unittest discover -s tests -p "test_*.py"
```

Use project-specific test commands when they are documented in README, package scripts, pyproject, or CI config.
"""


def _render_forbidden_actions() -> str:
    return """# Forbidden Actions

Hard safety boundary:

- project-scoped only
- no browser profile access
- no credential store access
- no external upload of raw traces, logs, screenshots, or network captures
- no CAPTCHA bypass
- no bot evasion
- no fingerprint spoofing
- no signature cracking
- no IP/account pool guidance
- no credential extraction
- no collection from real platforms unless the user provides explicit authorization

If a request asks for bypass, evasion, credential extraction, or unauthorized collection, stop and provide safe diagnostic or compliance-oriented next actions only.
"""


def _render_safety_policy() -> str:
    return """# Safety Policy

Before using raw logs or handoff outputs, run `failure-doctor safety-evaluate`.

Never read browser profiles.
Never read credential stores.
Never scan outside the project.
Never generate bypass, evasion, spoofing, cracking, challenge automation, or access-control defeat guidance.
If safety-evaluate blocks, stop and ask for manual review.
"""


def _render_safety_evaluation_workflow() -> str:
    return """# Safety Evaluation Workflow

Run:

```powershell
failure-doctor safety-evaluate --report .\\failure_doctor_auto_report --out .\\failure_doctor_auto_report\\safety_report
```

Read:

1. `safety_report/open_this_first_safety.md`
2. `safety_report/safety_evaluation_report.md`
3. `safety_report/shareability_decision.json`

Continue only when the report is pass or warning and the shareability decision is not blocked.
"""


def _render_regulated_workflow() -> str:
    return """# Regulated Workflow Evaluation

Use this for finance, government, healthcare, and other regulated-workflow mock
failures. This workflow uses synthetic local cases only.

```powershell
failure-doctor regulated-eval --suite all --out .\\regulated_report
```

Read:

1. `regulated_report\\regulated_eval_result.md`
2. `regulated_report\\regulated_eval_result.json`
3. `regulated_report\\regulated_cases.json`

This is not legal, medical, financial, or regulatory compliance advice. It is a
local evidence quality and shareability check. Do not connect to real regulated
systems, submit real forms, or include real patient, citizen, bank, or customer
data.
"""


def _render_visual_runtime_workflow() -> str:
    return """# Visual Runtime Workflow

Use this when an AI browser agent, RPA flow, Computer Use run, or screenshot-driven
automation fails after seeing a page.

Do not guess from the final screenshot only. First run an offline artifact check:

```powershell
failure-doctor visual-runtime diagnose --input .\\visual_run --out .\\visual_report --no-dom --safety-evaluate
```

Then inspect:

1. `visual_report\\open_this_first_visual.md`
2. `visual_report\\diagnosis.md`
3. `visual_report\\visual_timeline.md`
4. `visual_report\\coordinate_drift_report.json`
5. `visual_report\\stale_observation_report.json`
6. `visual_report\\screenshot_cost_report.json`

Check stale screenshots, DPR scaling, viewport scroll state, click coordinate
mapping, OCR/visual grounding, screenshot payload cost, and optional DOM conflict.

No screenshot upload unless the user has explicitly configured and authorized a
provider outside this local workflow.

Do not provide challenge defeat, anti-detection, fingerprint modification,
behavior imitation, pointer path generation for access-control defeat, or
automated challenge-solving instructions. If evidence is insufficient, request
manual review and a fuller local visual-run artifact.
"""


def _render_full_chain_evaluation_workflow() -> str:
    return """# Full-Chain Evaluation Workflow

Use this after local evidence has been collected and before asking an AI coding
assistant to make changes.

```powershell
failure-doctor full-chain-eval --input .\\failed_run --out .\\full_chain_report --include-safety --include-ocr --include-visual --include-regulated
```

Read:

1. `full_chain_report\\full_chain_evaluation.md`
2. `full_chain_report\\full_chain_evaluation.json`
3. `full_chain_report\\stage_results.json`

If unsafe handoff or unsafe sharing is blocked, sanitize first and do not paste
raw logs, screenshots, OCR text, cookies, tokens, or private data into any AI
frontend.
"""


def _render_ocr_evidence_workflow() -> str:
    return """# OCR Evidence Workflow

Use this when screenshots, PDFs, forms, tables, scanned reports, RPA exports,
ecommerce SKU tables, ERP exports, or document-heavy automation failures are
involved.

Run local/mock OCR evidence extraction first:

```powershell
failure-doctor ocr-evidence extract --input .\\failure_evidence --out .\\ocr_report --provider mock_ocr --safety-evaluate
```

Then compare local evidence when available:

```powershell
failure-doctor ocr-evidence compare --ocr .\\ocr_report --dom .\\dom_snapshot.html --out .\\ocr_dom_compare
failure-doctor ocr-evidence compare-vlm --ocr .\\ocr_report --vlm .\\vlm_responses.jsonl --out .\\ocr_vlm_compare
```

Rules:

1. Use OCR evidence as supporting evidence, not ground truth.
2. Do not upload screenshots or PDFs to cloud OCR unless the user explicitly
   authorized it and `failure-doctor safety-evaluate` has passed.
3. Do not include raw sensitive OCR text in AI handoff.
4. Use redacted OCR summaries and finding IDs.
5. Prefer DOM/schema/export comparison before asking an AI agent to edit code.
6. If sensitive customer, token, cookie, order, invoice, or personal data is
   detected, stop and sanitize before sharing.
"""


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
