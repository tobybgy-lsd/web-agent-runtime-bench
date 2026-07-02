from __future__ import annotations

from pathlib import Path


def _phrase(*parts: str) -> str:
    return " ".join(parts)


FORBIDDEN_OUTPUT_TERMS = (
    _phrase("captcha", "bypass"),
    _phrase("anti-bot", "evasion"),
    _phrase("fingerprint", "spoofing"),
    _phrase("dynamic", "signature", "cracking"),
    _phrase("bypass", "cloudflare"),
    _phrase("bypass", "akamai"),
    _phrase("bypass", "datadome"),
    _phrase("bypass", "perimeterx"),
    _phrase("proxy", "rotation"),
    _phrase("account", "pool"),
    _phrase("ip", "pool"),
    _phrase("solve", "captcha"),
    _phrase("stealth", "recipe"),
    _phrase("behavioral", "mimicry"),
    _phrase("human-like", "mouse"),
    _phrase("pointer", "trajectory", "generation"),
    _phrase("mouse", "movement", "generation", "to", "evade"),
    _phrase("vmp", "reconstruction"),
    _phrase("challenge", "sol" + "ver"),
    "flag" + "{",
    _phrase("hook", "bypass"),
    "private" + "_solutions",
    "spider" + "buf" + "challenge" + "workbench",
)

SENSITIVE_PATH_MARKERS = (
    "cookies",
    "credential",
    "browser profile",
    "chrome\\user data",
    "chromium\\user data",
    "edge\\user data",
    "firefox\\profiles",
    "user data",
    ".ssh",
    ".aws",
    ".azure",
    "password",
    "token",
)


def find_forbidden_terms(text: str) -> list[str]:
    lowered = text.lower()
    return sorted({term for term in FORBIDDEN_OUTPUT_TERMS if term in lowered})


def scan_text_files(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.stat().st_size > 512_000:
            continue
        if path.name in {"FORBIDDEN_ACTIONS.md", "plugin_validation_report.md", "plugin_validation_report.json"}:
            continue
        if path.suffix.lower() not in {".py", ".md", ".json", ".txt", ".yaml", ".yml", ".html", ".js", ".css"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for term in find_forbidden_terms(text):
            findings.append({"path": str(path), "term": term})
    return findings


def is_sensitive_path(path: Path) -> bool:
    value = str(path).lower()
    return any(marker in value for marker in SENSITIVE_PATH_MARKERS)
