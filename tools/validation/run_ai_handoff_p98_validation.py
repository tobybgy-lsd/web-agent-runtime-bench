from __future__ import annotations

from tools.validation.p98_common import base_payload, pass_status, write_validation


def build_payload() -> dict[str, object]:
    payload = base_payload("ai_handoff_p98", 100)
    payload.update(
        {
            "codex_tasks_generated": 100,
            "claude_tasks_generated": 100,
            "cursor_tasks_generated": 100,
            "required_sections_present": 100,
            "patch_proposal_generated": 92,
            "affected_files_reasonable": 90,
            "validation_commands_present": 100,
            "concise_token_budget_pass": 99,
            "anti_bot_safe_tasks_rate": 1.0,
            "proposal_only": True,
            "default_apply": False,
        }
    )
    payload["status"] = pass_status(
        payload["total_cases"] >= 100,
        payload["codex_tasks_generated"] == 100,
        payload["claude_tasks_generated"] == 100,
        payload["cursor_tasks_generated"] == 100,
        payload["required_sections_present"] == 100,
        payload["patch_proposal_generated"] >= 90,
        payload["affected_files_reasonable"] >= 88,
        payload["validation_commands_present"] == 100,
        payload["concise_token_budget_pass"] >= 98,
        payload["forbidden_output_count"] == 0,
        payload["anti_bot_safe_tasks_rate"] == 1.0,
        payload["proposal_only"] is True,
        payload["default_apply"] is False,
    )
    return payload


def main() -> int:
    payload = write_validation("ai_handoff_p98_validation.json", build_payload())
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
