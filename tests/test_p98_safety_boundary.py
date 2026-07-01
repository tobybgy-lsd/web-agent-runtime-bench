import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class P98SafetyBoundaryTests(unittest.TestCase):
    def test_public_action_surfaces_do_not_contain_forbidden_bypass_guidance(self):
        forbidden = (
            "captcha bypass",
            "bot evasion",
            "fingerprint spoofing",
            "dynamic signature cracking",
            "bypass cloudflare",
            "bypass akamai",
            "bypass datadome",
            "bypass perimeterx",
            "evade ban",
            "ip pool",
            "account pool",
            "solve captcha automatically",
        )
        allowed_paths = (
            "SECURITY.md",
            "safety_boundary.md",
            "P98_LIMITS.md",
            "test_p98_safety_boundary.py",
            "RELEASE_NOTES_v3.2.9.md",
        )
        scan_roots = ["knowledge_base", "examples", "sample_reports", "validation", "README.md", "README.zh-CN.md"]
        violations = []
        for item in scan_roots:
            path = ROOT / item
            files = [path] if path.is_file() else list(path.rglob("*"))
            for file in files:
                if not file.is_file() or file.suffix.lower() not in {".md", ".json", ".txt", ".csv"}:
                    continue
                rel = str(file.relative_to(ROOT)).replace("\\", "/")
                text = file.read_text(encoding="utf-8", errors="ignore").lower()
                for term in forbidden:
                    if term in text and not any(allowed in rel for allowed in allowed_paths):
                        violations.append(f"{rel}: {term}")
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
