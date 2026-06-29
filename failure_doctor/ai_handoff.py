from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping
from zipfile import ZIP_DEFLATED, ZipFile


TARGETS = ("codex", "claude_code", "cursor")
FORBIDDEN_ACTIONS = (
    "access-control defeat",
    "challenge automation",
    "credential extraction",
    "unauthorized collection",
    "bot evasion",
)


def write_ai_handoff_pack(report_dir: Path, out_dir: Path, *, target: str) -> dict[str, Any]:
    if target not in TARGETS and target != "all":
        raise ValueError(f"unsupported handoff target: {target}")

    context = load_report_context(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    generated: dict[str, Path] = {}
    for task_target in TARGETS:
        path = out_dir / f"{task_target}_task.md"
        path.write_text(render_task(context, task_target), encoding="utf-8")
        generated[path.name] = path

    affected = affected_files_payload(context)
    validation = validation_commands(context)
    forbidden = forbidden_actions_payload()
    token_budget = token_budget_payload(context, target)
    handoff_summary = ai_handoff_summary(context, target, token_budget)

    write_json(out_dir / "affected_files.json", affected)
    (out_dir / "validation_commands.md").write_text(render_validation_commands(validation), encoding="utf-8")
    (out_dir / "forbidden_actions.md").write_text(render_forbidden_actions(forbidden), encoding="utf-8")
    write_json(out_dir / "token_budget_report.json", token_budget)
    write_json(out_dir / "ai_handoff.json", handoff_summary)
    (out_dir / "ai_handoff.md").write_text(render_ai_handoff_markdown(handoff_summary), encoding="utf-8")
    zip_path = out_dir / "ai_handoff_pack.zip"
    write_zip(out_dir, zip_path)

    return {
        "schema_version": "ai_handoff_pack/v1",
        "selected_target": target,
        "source_report": str(report_dir),
        "out_dir": str(out_dir),
        "files": sorted(path.name for path in out_dir.iterdir() if path.is_file()),
        "zip_path": str(zip_path),
        "token_budget": token_budget,
    }


def write_patch_proposal(repo_dir: Path, report_dir: Path, out_dir: Path) -> dict[str, Any]:
    if not repo_dir.exists():
        raise FileNotFoundError(f"repo not found: {repo_dir}")

    context = load_report_context(report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    affected = affected_files_payload(context, repo_dir=repo_dir)
    validation = validation_commands(context)
    proposal = proposed_changes_payload(context, report_dir)
    risk = patch_risk_payload(context)

    (out_dir / "patch_proposal.md").write_text(render_patch_proposal(context, proposal), encoding="utf-8")
    write_json(out_dir / "proposed_changes.json", proposal)
    write_json(out_dir / "affected_files.json", affected)
    (out_dir / "validation_commands.md").write_text(render_validation_commands(validation), encoding="utf-8")
    write_json(out_dir / "patch_risk_assessment.json", risk)

    return {
        "schema_version": "patch_proposal_pack/v1",
        "source_report": str(report_dir),
        "repo": str(repo_dir),
        "out_dir": str(out_dir),
        "dry_run_only": True,
        "files": sorted(path.name for path in out_dir.iterdir() if path.is_file()),
    }


def load_report_context(report_dir: Path) -> dict[str, Any]:
    if not report_dir.exists():
        raise FileNotFoundError(f"report not found: {report_dir}")
    diagnosis = read_json(report_dir / "diagnosis.json")
    fix_plan = read_json(report_dir / "fix_plan.json") if (report_dir / "fix_plan.json").exists() else {}
    evidence_graph = read_json(report_dir / "evidence_graph.json") if (report_dir / "evidence_graph.json").exists() else {}
    evidence = read_json(report_dir / "evidence.json") if (report_dir / "evidence.json").exists() else {}
    return {
        "report_dir": str(report_dir),
        "diagnosis": diagnosis,
        "fix_plan": fix_plan,
        "evidence_graph": evidence_graph,
        "evidence": evidence,
    }


def render_task(context: Mapping[str, Any], target: str) -> str:
    diagnosis = _diagnosis(context)
    plan = _fix_plan(context)
    target_name = {"codex": "Codex", "claude_code": "Claude Code", "cursor": "Cursor"}[target]
    repair_order = _bullets(plan.get("repair_order", [])) or "- Follow the root cause and fix intent first."
    areas = _bullets(plan.get("recommended_change_area", [])) or "- Locate the smallest code area that owns this automation failure."
    evidence = _bullets(diagnosis.get("evidence", [])) or "- See diagnosis.json and evidence_graph.json."
    validation = _bullets(validation_commands(context)["commands"])
    forbidden = _bullets(FORBIDDEN_ACTIONS)
    return "\n".join(
        [
            f"# {target_name} Repair Task",
            "",
            "Use this as an AI coding assistant task. Do not apply changes automatically from Agent Failure Doctor; inspect the repository first and make the smallest safe edit.",
            "",
            "## Diagnosis",
            "",
            f"- Technical category: `{_technical_category(diagnosis)}`",
            f"- Subtype: `{diagnosis.get('subtype', '')}`",
            f"- Failure layer: `{diagnosis.get('failure_layer', plan.get('failure_layer', 'unknown'))}`",
            f"- Confidence: `{diagnosis.get('confidence', '')}`",
            "",
            "## Evidence",
            "",
            evidence,
            "",
            "## Fix Intent",
            "",
            str(plan.get("fix_intent") or "Create a minimal fix based on the diagnosis and evidence."),
            "",
            "## Repair order",
            "",
            repair_order,
            "",
            "## Recommended change area",
            "",
            areas,
            "",
            "## Validation",
            "",
            validation,
            "- After editing, run `failure-doctor verify --before <before> --after <after> --out <verification_report>` when after-run evidence exists.",
            "",
            "## Forbidden actions",
            "",
            forbidden,
            "- Do not store raw credentials, cookies, tokens, private traces, or sensitive screenshots in the repository.",
        ]
    )


def ai_handoff_summary(
    context: Mapping[str, Any],
    target: str,
    token_budget: Mapping[str, Any],
) -> dict[str, Any]:
    diagnosis = _diagnosis(context)
    plan = _fix_plan(context)
    repair_order = [str(item) for item in plan.get("repair_order", [])] if isinstance(plan.get("repair_order"), list) else []
    required_sections = {
        "diagnosis": bool(_technical_category(diagnosis)),
        "evidence": bool(diagnosis.get("evidence") or context.get("evidence_graph")),
        "fix_intent": bool(plan.get("fix_intent") or repair_order),
        "repair_order": bool(repair_order or plan.get("recommended_change_area")),
        "validation": True,
        "forbidden_actions": True,
    }
    return {
        "schema_version": "ai_handoff/v1",
        "selected_target": target,
        "source_report": str(context.get("report_dir", "")),
        "technical_category": _technical_category(diagnosis),
        "subtype": diagnosis.get("subtype", ""),
        "failure_layer": diagnosis.get("failure_layer", plan.get("failure_layer", "unknown")),
        "repair_order": repair_order,
        "tasks": {
            "codex": "codex_task.md",
            "claude_code": "claude_code_task.md",
            "cursor": "cursor_task.md",
        },
        "validation_commands": validation_commands(context)["commands"],
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "token_budget": dict(token_budget),
        "required_sections": required_sections,
        "required_sections_present": all(required_sections.values()),
        "proposal_only": True,
    }


def render_ai_handoff_markdown(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AI Handoff",
            "",
            f"- Selected target: `{summary.get('selected_target')}`",
            f"- Technical category: `{summary.get('technical_category')}`",
            f"- Subtype: `{summary.get('subtype')}`",
            f"- Proposal only: `{summary.get('proposal_only')}`",
            "",
            "## Task Files",
            "",
            _bullets([f"{target}: {path}" for target, path in dict(summary.get("tasks", {})).items()]),
            "",
            "## Repair order",
            "",
            _bullets(summary.get("repair_order", [])) or "- See the target task file for recommended order.",
            "",
            "## Validation",
            "",
            _bullets(summary.get("validation_commands", [])),
            "",
            "## Forbidden actions",
            "",
            _bullets(summary.get("forbidden_actions", [])),
            "",
        ]
    )


def render_patch_proposal(context: Mapping[str, Any], proposal: Mapping[str, Any]) -> str:
    diagnosis = _diagnosis(context)
    plan = _fix_plan(context)
    steps = _bullets(proposal.get("change_steps", []))
    files = _bullets(proposal.get("candidate_files", [])) or "- No exact files inferred; inspect the owner of the failing automation flow."
    return "\n".join(
        [
            "# Patch Proposal",
            "",
            "Mode: proposal only. This command does not edit source files, apply patches, run tests, or open a pull request.",
            "",
            "## Diagnosis",
            "",
            f"- Technical category: `{_technical_category(diagnosis)}`",
            f"- Subtype: `{diagnosis.get('subtype', '')}`",
            f"- Root cause: `{plan.get('root_cause', '')}`",
            "",
            "## Proposed change steps",
            "",
            steps,
            "",
            "## Candidate files or areas",
            "",
            files,
            "",
            "## Verification",
            "",
            _bullets(validation_commands(context)["commands"]),
            "",
            "## Safety boundary",
            "",
            "- Keep this as a dry-run proposal until a human or AI coding assistant reviews the repository.",
            "- Do not implement challenge automation, access-control defeat, credential extraction, bot evasion, or unauthorized collection.",
        ]
    )


def proposed_changes_payload(context: Mapping[str, Any], report_dir: Path) -> dict[str, Any]:
    diagnosis = _diagnosis(context)
    plan = _fix_plan(context)
    areas = [str(item) for item in plan.get("recommended_change_area", []) if item]
    steps = list(plan.get("repair_order", [])) if isinstance(plan.get("repair_order"), list) else []
    if not steps:
        steps = [
            f"Inspect the code that owns: {', '.join(areas) if areas else _technical_category(diagnosis)}.",
            str(plan.get("fix_intent") or "Apply the smallest safe change that matches the evidence."),
            "Add or update a regression test for this failure mode.",
            "Capture an after-run artifact and verify it with failure-doctor verify.",
        ]
    return {
        "schema_version": "patch_proposal/v1",
        "source_report": str(report_dir),
        "dry_run_only": True,
        "applied": False,
        "technical_category": _technical_category(diagnosis),
        "subtype": diagnosis.get("subtype", ""),
        "change_steps": steps,
        "candidate_files": candidate_files_from_areas(areas),
        "validation_commands": validation_commands(context)["commands"],
    }


def affected_files_payload(context: Mapping[str, Any], repo_dir: Path | None = None) -> dict[str, Any]:
    plan = _fix_plan(context)
    areas = [str(item) for item in plan.get("recommended_change_area", []) if item]
    return {
        "schema_version": "affected_files/v1",
        "repo": str(repo_dir) if repo_dir else None,
        "inference_level": "area_hint",
        "recommended_change_area": areas,
        "candidate_files": candidate_files_from_areas(areas),
        "notes": [
            "These are patch-planning hints, not a guarantee.",
            "Inspect the repository before editing.",
        ],
    }


def validation_commands(context: Mapping[str, Any]) -> dict[str, Any]:
    plan = _fix_plan(context)
    commands = [
        "python -m unittest discover -s tests -p \"test_*.py\"",
        "powershell -ExecutionPolicy Bypass -File scripts\\smoke_test.ps1",
        "powershell -ExecutionPolicy Bypass -File scripts\\local_safety_scan.ps1",
    ]
    if _technical_category(_diagnosis(context)) == "playwright_storage_state_context":
        commands.insert(0, "rerun the affected Playwright test with trace/log capture enabled")
    strategy = plan.get("verification_strategy")
    if strategy:
        commands.append(f"manual evidence check: {strategy}")
    return {"schema_version": "validation_commands/v1", "commands": commands}


def token_budget_payload(context: Mapping[str, Any], target: str) -> dict[str, Any]:
    combined = json.dumps(
        {
            "diagnosis": _diagnosis(context),
            "fix_plan": _fix_plan(context),
            "evidence_graph": context.get("evidence_graph", {}),
        },
        ensure_ascii=False,
    )
    estimated = max(1, len(combined) // 4)
    return {
        "schema_version": "token_budget_report/v1",
        "selected_target": target,
        "estimated_input_tokens": estimated,
        "recommended_budget": max(4000, estimated + 1200),
        "truncation_policy": "Prefer diagnosis, fix_plan, repair_order, and evidence_graph summary before raw logs.",
    }


def patch_risk_payload(context: Mapping[str, Any]) -> dict[str, Any]:
    plan = _fix_plan(context)
    return {
        "schema_version": "patch_risk_assessment/v1",
        "mode": "proposal_only",
        "auto_apply": False,
        "risk": plan.get("risk", "unknown"),
        "failure_layer": plan.get("failure_layer", _diagnosis(context).get("failure_layer", "unknown")),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "review_required": True,
    }


def forbidden_actions_payload() -> dict[str, Any]:
    return {
        "schema_version": "forbidden_actions/v1",
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "policy": "diagnosis and patch planning only; no bypass, credential, or unauthorized collection implementation",
    }


def candidate_files_from_areas(areas: list[str]) -> list[str]:
    candidates: list[str] = []
    mapping = {
        "storage": ["auth setup", "global setup", "browser context factory", "storageState file owner"],
        "browser context": ["browser context factory", "test fixture setup"],
        "selectors": ["page object", "locator definitions", "affected test file"],
        "locator": ["page object", "locator definitions", "affected test file"],
        "route": ["network mock setup", "route/HAR registration"],
        "har": ["HAR replay setup", "network mock setup"],
        "proxy": ["environment config", "CI config", "proxy setup"],
        "dns": ["environment config", "network setup"],
        "tls": ["certificate configuration", "network setup"],
    }
    for area in areas:
        lower = area.lower()
        matched = False
        for marker, values in mapping.items():
            if marker in lower:
                candidates.extend(values)
                matched = True
        if not matched:
            candidates.append(area)
    return sorted(dict.fromkeys(candidates))


def render_validation_commands(payload: Mapping[str, Any]) -> str:
    return "\n".join(["# Validation Commands", "", _bullets(payload.get("commands", [])), ""])


def render_forbidden_actions(payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Forbidden Actions",
            "",
            _bullets(payload.get("forbidden_actions", [])),
            "",
            str(payload.get("policy", "")),
            "",
        ]
    )


def write_zip(root: Path, zip_path: Path) -> None:
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for path in sorted(root.iterdir()):
            if path == zip_path or not path.is_file():
                continue
            archive.write(path, path.name)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"required report file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _diagnosis(context: Mapping[str, Any]) -> Mapping[str, Any]:
    return context.get("diagnosis", {}) if isinstance(context.get("diagnosis"), Mapping) else {}


def _fix_plan(context: Mapping[str, Any]) -> Mapping[str, Any]:
    return context.get("fix_plan", {}) if isinstance(context.get("fix_plan"), Mapping) else {}


def _technical_category(diagnosis: Mapping[str, Any]) -> str:
    return str(diagnosis.get("technical_category") or diagnosis.get("failure_type") or "unknown")


def _bullets(items: Any) -> str:
    if not isinstance(items, list):
        return ""
    return "\n".join(f"- {item}" for item in items)
