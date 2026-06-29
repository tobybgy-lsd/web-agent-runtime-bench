import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    ROOT / "examples" / "applied_scenarios",
    ROOT / "validation" / "applied_scenario_validation.json",
]

FORBIDDEN_ACTION_TERMS = [
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
    re.compile(r"\b1[3-9]\d{9}\b"),
    re.compile(r"\b\d{17}[\dXx]\b"),
]

REAL_PLATFORM_DOMAINS = [
    "taobao.com",
    "tmall.com",
    "jd.com",
    "pinduoduo.com",
    "douyin.com",
    "xiaohongshu.com",
    "kingdee.com",
    "yonyou.com",
]


def iter_text_files():
    for root in SCAN_ROOTS:
        if root.is_file() and root.exists():
            yield root
        elif root.exists():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".md", ".txt", ".log", ".json", ".jsonl", ".csv", ".html", ".py"}:
                    yield path


class AppliedScenarioSafetyTests(unittest.TestCase):
    def test_applied_scenarios_do_not_contain_bypass_guidance_or_secrets(self):
        offenders = []
        for path in iter_text_files():
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for term in FORBIDDEN_ACTION_TERMS:
                if term.lower() in lowered:
                    offenders.append(f"{path}: forbidden action term {term}")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    offenders.append(f"{path}: secret-like pattern {pattern.pattern}")
            for domain in REAL_PLATFORM_DOMAINS:
                if domain in lowered:
                    offenders.append(f"{path}: real platform domain {domain}")
        self.assertEqual(offenders, [])

    def test_applied_scenario_docs_say_local_only_mock_not_production_system(self):
        docs = [
            ROOT / "examples" / "applied_scenarios" / "README.md",
            ROOT / "docs" / "APPLIED_SCENARIO_DEMOS.md",
        ]
        for path in docs:
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("local-only", text, str(path))
            self.assertIn("mock", text, str(path))
            self.assertIn("not a production", text, str(path))


if __name__ == "__main__":
    unittest.main()
