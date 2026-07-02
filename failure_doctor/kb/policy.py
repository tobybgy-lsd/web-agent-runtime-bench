from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "failure_kb/v1"
CASE_SCHEMA_VERSION = "failure_kb_case/v1"
TOOL_VERSION = "3.9.0"

SOURCE_VALUES = {
    "local_sanitized_report",
    "synthetic_fixture",
    "user_imported_sanitized",
    "ci_sanitized_artifact",
}

PRIVATE_MARKERS = (
    "raw_local_only_do_not_share",
    "private_" + "solutions",
    "Spiderbuf" + "ChallengeWorkbench",
    "Codex" + "Vault",
    "FLAG" + "{",
    "closed_book" + "_exam",
    "browser" + "_executor",
    "mock challenge " + "server",
    "VMP " + "restore",
    "private " + "solution",
    "challenge " + "pass",
)

FORBIDDEN_MARKERS = (
    "captcha " + "bypass",
    "anti-bot " + "evasion",
    "fingerprint " + "spoofing",
    "dynamic signature " + "cracking",
    "bypass " + "cloudflare",
    "bypass " + "akamai",
    "bypass " + "datadome",
    "bypass " + "perimeterx",
    "proxy " + "rotation",
    "account " + "pool",
    "ip " + "pool",
    "solve " + "captcha",
    "stealth " + "recipe",
    "behavioral " + "mimicry",
    "human-like " + "mouse",
    "trajectory " + "generator",
    "challenge " + "sol" + "ver",
    "hook " + "bypass",
)

SECRET_MARKERS = (
    "authorization:",
    "bearer ",
    "api_key",
    "api key",
    "cookie:",
    "set-cookie",
    "password",
    "secret=",
    "token=",
)


def assess_text_safety(text: str) -> dict[str, Any]:
    lower = text.lower()
    private_hits = [item for item in PRIVATE_MARKERS if item.lower() in lower]
    forbidden_hits = [item for item in FORBIDDEN_MARKERS if item.lower() in lower]
    secret_hits = [item for item in SECRET_MARKERS if item.lower() in lower]
    blocked = bool(private_hits or forbidden_hits or secret_hits)
    return {
        "shareability_decision": "blocked" if blocked else "safe_to_share",
        "contains_raw_secret": bool(secret_hits),
        "contains_private_solution": bool(private_hits),
        "contains_forbidden_guidance": bool(forbidden_hits),
        "anti_bot_boundary": "anti_bot" in lower or "captcha" in lower or "fingerprint" in lower,
        "matched_private_markers": private_hits,
        "matched_forbidden_markers": forbidden_hits,
        "matched_secret_markers": secret_hits,
    }


def is_importable_safety(safety: dict[str, Any]) -> bool:
    return (
        safety.get("shareability_decision") in {"safe_to_share", "sanitize_required"}
        and not safety.get("contains_raw_secret")
        and not safety.get("contains_private_solution")
        and not safety.get("contains_forbidden_guidance")
    )


def safe_next_action_for(failure_type: str, subtype: str, fallback: str = "") -> str:
    text = f"{failure_type} {subtype}".lower()
    if "anti_bot" in text or "fingerprint" in text or "captcha" in text:
        return (
            "Treat this as a compliance boundary. Confirm authorization, use official APIs "
            "or export paths, collect safe evidence, and stop automation when authorization is unclear."
        )
    return fallback or "Use this historical case as an evidence-backed suggestion; verify before changing code."
