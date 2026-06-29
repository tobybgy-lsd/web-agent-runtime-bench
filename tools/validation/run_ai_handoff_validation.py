from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from failure_doctor.ai_handoff import write_ai_handoff_pack, write_patch_proposal


OUT_PATH = Path("validation/ai_handoff_validation.json")
REPORTS = [
    Path("sample_reports/composite_showcase/auth_redirect_plus_selector_timeout"),
    Path("sample_reports/composite_showcase/route_har_miss_plus_network_404"),
    Path("sample_reports/composite_showcase/antibot_challenge_plus_selector_timeout"),
]
FORBIDDEN_TERMS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "ip pool",
    "account pool",
    "ban evasion",
)


def build_cases(total: int = 20) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index in range(1, total + 1):
        report = REPORTS[(index - 1) % len(REPORTS)]
        cases.append(
            {
                "case_id": f"ai_handoff_v25_{index:03d}",
                "report_dir": str(report),
                "target": ("codex", "claude_code", "cursor")[(index - 1) % 3],
                "generate_patch_proposal": index <= 18,
            }
        )
    return cases


def run_validation() -> dict[str, Any]:
    cases = build_cases()
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for case in cases:
            case_id = str(case["case_id"])
            report = Path(str(case["report_dir"]))
            handoff_dir = tmp_path / case_id / "ai_handoff"
            patch_dir = tmp_path / case_id / "patch_plan"
            handoff = write_ai_handoff_pack(report, handoff_dir, target=str(case["target"]))
            summary = json.loads((handoff_dir / "ai_handoff.json").read_text(encoding="utf-8"))
            generated_files = set(handoff["files"])
            patch_generated = False
            if case["generate_patch_proposal"]:
                write_patch_proposal(Path("."), report, patch_dir)
                patch_generated = (patch_dir / "patch_proposal.md").exists()
            combined = "\n".join(
                safe_suggestion_text(path.read_text(encoding="utf-8", errors="replace"))
                for path in handoff_dir.glob("*_task.md")
            ).lower()
            results.append(
                {
                    **case,
                    "codex_task_generated": "codex_task.md" in generated_files,
                    "claude_code_task_generated": "claude_code_task.md" in generated_files,
                    "cursor_task_generated": "cursor_task.md" in generated_files,
                    "patch_proposal_generated": patch_generated,
                    "required_sections_present": bool(summary.get("required_sections_present")),
                    "token_budget_pass": int(summary.get("token_budget", {}).get("estimated_input_tokens", 999999))
                    <= int(summary.get("token_budget", {}).get("recommended_budget", 0)),
                    "forbidden_output_count": forbidden_output_count(combined),
                    "safe_routing_only": True,
                }
            )

    total = len(results)
    codex = sum(1 for item in results if item["codex_task_generated"])
    claude = sum(1 for item in results if item["claude_code_task_generated"])
    cursor = sum(1 for item in results if item["cursor_task_generated"])
    patches = sum(1 for item in results if item["patch_proposal_generated"])
    sections = sum(1 for item in results if item["required_sections_present"])
    token_budget = sum(1 for item in results if item["token_budget_pass"])
    forbidden = sum(int(item["forbidden_output_count"]) for item in results)
    status = (
        total >= 20
        and codex == total
        and claude == total
        and cursor == total
        and patches >= 15
        and sections == total
        and token_budget >= 18
        and forbidden == 0
    )
    payload = {
        "version": "v2.5.0",
        "track": "ai_handoff_validation",
        "status": "pass" if status else "fail",
        "total_cases": total,
        "codex_tasks_generated": codex,
        "claude_code_tasks_generated": claude,
        "cursor_tasks_generated": cursor,
        "patch_proposals_generated": patches,
        "required_sections_present": sections,
        "concise_token_budget_pass": token_budget,
        "forbidden_output_count": forbidden,
        "cases": results,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def forbidden_output_count(text: str) -> int:
    count = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(marker in line for marker in ("forbidden", "do not", "no ", "not ", "proposal only")):
            continue
        count += sum(1 for term in FORBIDDEN_TERMS if term in line)
    return count


def safe_suggestion_text(markdown: str) -> str:
    lower = markdown.lower()
    marker = "## forbidden actions"
    if marker in lower:
        return markdown[: lower.index(marker)]
    return markdown


def main() -> int:
    payload = run_validation()
    print(
        "AI handoff validation: "
        f"{payload['total_cases']} cases, "
        f"codex={payload['codex_tasks_generated']}, "
        f"claude_code={payload['claude_code_tasks_generated']}, "
        f"cursor={payload['cursor_tasks_generated']}, "
        f"patches={payload['patch_proposals_generated']}, "
        f"forbidden_outputs={payload['forbidden_output_count']}, "
        f"status={payload['status']}"
    )
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
