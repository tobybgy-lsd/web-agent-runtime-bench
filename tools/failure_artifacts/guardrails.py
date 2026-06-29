"""Shared output-safety guardrails for diagnosis artifacts.

The terms here are deliberately narrow phrases that should not appear as
recommended actions. Keep boundary language in docs/report prompts positive
and compliant instead of repeating unsafe how-to terms.
"""

from __future__ import annotations


FORBIDDEN_OUTPUT_TERMS = (
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "cloudflare bypass",
    "akamai bypass",
    "datadome bypass",
    "perimeterx bypass",
    "kasada bypass",
    "ip pool",
    "account pool",
    "ban evasion",
    "bypass rate limit",
    "evade rate limit",
    "proxy rotation for evasion",
    "residential proxy rotation",
    "webdriver stealth",
    "undetected chromedriver",
    "patch navigator.webdriver",
    "solve captcha automatically",
    "captcha solving service",
    "fake device fingerprint",
    "canvas spoofing",
    "webgl spoofing",
    "tls fingerprint spoofing",
    "ja3 spoofing",
    "reverse engineer signature",
    "crack signature",
    "replay protected signature",
    "generate x-bogus",
    "x-bogus generation",
    "generate x-s",
    "x-s generation",
    "cookie theft",
    "token extraction",
    "credential extraction",
    "绕过验证码",
    "绕过风控",
    "伪造指纹",
    "破解签名",
    "规避封禁",
    "批量过验证码",
)


def forbidden_output_hits(text: str) -> list[str]:
    lowered = str(text).lower()
    return [term for term in FORBIDDEN_OUTPUT_TERMS if term in lowered]


def forbidden_output_count(text: str) -> int:
    return len(forbidden_output_hits(text))
