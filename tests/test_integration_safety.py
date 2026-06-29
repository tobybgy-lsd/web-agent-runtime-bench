import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    ROOT / "integrations",
    ROOT / "docs" / "GITHUB_ACTION_USAGE.md",
    ROOT / "docs" / "INTEGRATIONS.md",
]

FORBIDDEN_TERMS = [
    "captcha bypass",
    "bot evasion",
    "fingerprint spoofing",
    "dynamic signature cracking",
    "bypass cloudflare",
    "evade ban",
    "ip pool",
    "account pool",
    "solve captcha automatically",
    "批量养号",
    "绕过审核",
    "绕过验证码",
    "绕过风控",
    "伪造指纹",
    "破解签名",
    "规避封禁",
    "批量过验证码",
]

SECRET_PATTERNS = [
    re.compile(r"authorization\s*:", re.IGNORECASE),
    re.compile(r"\bcookie\s*:", re.IGNORECASE),
    re.compile(r"\btoken\s*[:=]\s*['\"]?[A-Za-z0-9_\-.]{12,}", re.IGNORECASE),
]


def iter_files():
    for root in SCAN_ROOTS:
        if root.is_file() and root.exists():
            yield root
        elif root.exists():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".py", ".md", ".yml", ".yaml", ".json", ".txt"}:
                    yield path


class IntegrationSafetyTests(unittest.TestCase):
    def test_integrations_do_not_include_bypass_guidance_or_secrets(self):
        offenders = []
        for path in iter_files():
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for term in FORBIDDEN_TERMS:
                if term.lower() in lowered:
                    offenders.append(f"{path}: forbidden term {term}")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    offenders.append(f"{path}: secret-like pattern {pattern.pattern}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
