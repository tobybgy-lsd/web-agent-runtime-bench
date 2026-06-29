import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    ROOT / "examples" / "spiderbuf_inspired_challenges",
    ROOT / "validation" / "spiderbuf_inspired_validation.json",
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
    "cloudflare bypass",
    "proxy pool",
    "signing crack",
    "signature cracking",
]

SECRET_PATTERNS = [
    re.compile(r"authorization\s*:", re.IGNORECASE),
    re.compile(r"\bcookie\s*:", re.IGNORECASE),
    re.compile(r"\btoken\s*[:=]\s*['\"]?[A-Za-z0-9_\-.]{12,}", re.IGNORECASE),
]


def iter_text_files():
    for root in SCAN_ROOTS:
        if root.is_file() and root.exists():
            yield root
        elif root.exists():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".md", ".txt", ".log", ".json", ".csv", ".py"}:
                    yield path


class SpiderbufInspiredSafetyTests(unittest.TestCase):
    def test_pack_does_not_contain_bypass_guidance_or_secrets(self):
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
        self.assertEqual(offenders, [])

    def test_pack_docs_state_local_only_mock_and_diagnosis_only(self):
        readme = (ROOT / "examples" / "spiderbuf_inspired_challenges" / "README.md").read_text(
            encoding="utf-8"
        )
        lowered = readme.lower()
        self.assertIn("local-only", lowered)
        self.assertIn("mock", lowered)
        self.assertIn("diagnosis-only", lowered)
        self.assertIn("does not access spiderbuf.cn", lowered)


if __name__ == "__main__":
    unittest.main()
