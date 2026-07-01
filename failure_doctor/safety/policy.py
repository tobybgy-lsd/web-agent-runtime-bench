from __future__ import annotations

SAFE_NEXT_ACTIONS = [
    "Keep the review local-only.",
    "Sanitize raw logs, screenshots, network summaries, and handoff prompts before sharing.",
    "Use official APIs, authorized exports, or manual review when access-control risk appears.",
    "Stop automation if authorization is unclear.",
]

FORBIDDEN_ACTIONS = [
    "CAPTCHA bypass",
    "anti-bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "protected signature reconstruction",
    "proxy rotation guidance",
    "IP pool or account pool guidance",
    "browser stealth " + "recipes",
    "behavioral mimicry steps",
    "runtime alteration recipes",
    "VMP reconstruction",
    "challenge completion automation",
    "credential extraction",
    "browser profile reading",
    "credential store reading",
    "whole-computer scanning",
    "unauthorized access",
]

UNSAFE_HANDOFF_PATTERNS = [
    "read browser cookies",
    "read credential store",
    "scan whole computer",
    "bypass captcha",
    "evade anti-bot",
    "spoof fingerprint",
    "generate signature",
    "crack signature",
    "proxy pool",
    "account pool",
    "modify webgl",
    "modify webrtc",
    "pointer trajectory",
    "reconstruct vmp",
    "restore vm logic",
    "extract token",
]

UNSAFE_PATCH_PATTERNS = [
    "stealth " + "patch",
    "fingerprint spoofing",
    "captcha automation",
    "challenge bypass",
    "signature cracking",
    "credential extraction",
    "browser profile reader",
    "proxy rotation",
    "account rotation",
    "raw secret logging",
]

PRIVATE_CONTENT_PATTERNS = [
    "tools/" + "spiderbuf",
    "spiderbuf" + "challengeworkbench",
    "closed_book" + "_exam",
    "browser" + "_executor",
    "mock challenge " + "server",
    "private " + "solution",
    "challenge " + "pass",
    "flag" + "{",
    "vmp " + "restore",
    "hook " + "bypass",
]
