from __future__ import annotations

from typing import Any


FORBIDDEN_TERMS = (
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
    "pointer trajectory generation",
    "mouse movement generation " + "to evade",
    "VMP " + "reconstruction",
    "challenge " + "sol" + "ver",
    "hook " + "bypass",
)

SECRET_TERMS = ("authorization:", "bearer ", "set-cookie", "cookie:", "api_key", "token=", "password")
PRIVATE_TERMS = (
    "Spiderbuf" + "ChallengeWorkbench",
    "FLAG" + "{",
    "private " + "solution",
    "challenge " + "pass",
    "private training " + "solution",
)


def scan_text(text: str) -> dict[str, Any]:
    lower = text.lower()
    forbidden = [term for term in FORBIDDEN_TERMS if term.lower() in lower]
    secrets = [term for term in SECRET_TERMS if term.lower() in lower]
    private = [term for term in PRIVATE_TERMS if term.lower() in lower]
    return {
        "is_allowed": not (forbidden or secrets or private),
        "forbidden_hits": forbidden,
        "secret_hits": secrets,
        "private_hits": private,
    }
