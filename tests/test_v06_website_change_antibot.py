import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import enrich_for_users
from tools.failure_artifacts.classifier import classify_failure_artifact


ROOT = Path(__file__).resolve().parents[1]


def artifact_with(text: str, observations: dict | None = None, status_code: int | None = None) -> dict:
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": "v06_test",
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": text,
        "error": {"message": text, "status_code": status_code},
        "observations": observations or {},
        "expected": {"required_fields": ["title", "price"]},
        "actual": {"fields": {}},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {"sanitized": True},
    }


class WebsiteChangeAndAntiBotRiskTests(unittest.TestCase):
    def test_website_change_subtypes(self):
        cases = {
            "selector_drift": artifact_with(
                "old selector not found after deployment",
                {"old_selector_missing": True, "similar_dom_candidate": "button[data-testid=submit]"},
            ),
            "dom_structure_changed": artifact_with(
                "DOM snapshot changed, container moved under app shell",
                {"dom_structure_changed": True, "old_dom_path": "#main form", "new_dom_path": "main section form"},
            ),
            "api_endpoint_changed": artifact_with(
                "request returned 404 for old endpoint /api/v1/products and 301 to /api/v2/products",
                {"api_endpoint_changed": True, "old_endpoint": "/api/v1/products", "new_endpoint": "/api/v2/products"},
            ),
            "response_shape_changed": artifact_with(
                "schema validation failed because JSON key price is missing",
                {"response_shape_changed": True, "missing_json_keys": ["price"], "new_json_keys": ["amount"]},
            ),
            "graphql_schema_changed": artifact_with(
                "GraphQL error: Cannot query field productPrice on type Product",
                {"graphql_error": "Cannot query field productPrice on type Product"},
            ),
            "pagination_changed": artifact_with(
                "pagination next cursor missing after website release",
                {"pagination_changed": True, "missing_cursor": "nextCursor"},
            ),
            "login_flow_changed": artifact_with(
                "login flow changed; new MFA consent page appears before dashboard",
                {"login_flow_changed": True, "new_step": "mfa_consent"},
            ),
            "download_behavior_changed": artifact_with(
                "download changed from direct link to async export job",
                {"download_behavior_changed": True, "old_download_mode": "direct_link", "new_download_mode": "async_job"},
            ),
        }

        for subtype, artifact in cases.items():
            with self.subTest(subtype=subtype):
                diagnosis = classify_failure_artifact(artifact)
                public = enrich_for_users(diagnosis)

                self.assertEqual(diagnosis["failure_type"], "website_change")
                self.assertEqual(diagnosis["subtype"], subtype)
                self.assertEqual(public["technical_category"], "website_change")
                self.assertEqual(public["failure_layer"], "website_change")
                self.assertEqual(public["user_facing_category"], "网站结构变化")

    def test_anti_bot_risk_subtypes_are_safe(self):
        cases = {
            "rate_limited": artifact_with("HTTP 429 too many requests after repeated runs", status_code=429),
            "captcha_or_challenge_page": artifact_with("challenge page says verify you are human with captcha"),
            "fingerprint_risk": artifact_with("headless browser blocked while headed run succeeds", {"headless_headed_mismatch": True}),
            "dynamic_signature_required": artifact_with("request failed because signature token x-bogus is invalid"),
            "ip_reputation_block": artifact_with("access denied from current network, works from approved office network"),
            "behavioral_risk": artifact_with("short time large request burst triggered unusual traffic warning"),
            "auth_or_permission_block": artifact_with("HTTP 403 after login; account lacks permission", status_code=403),
        }

        forbidden = (
            "bypass captcha",
            "captcha bypass",
            "bot evasion",
            "spoof fingerprint",
            "fingerprint spoofing",
            "crack signature",
            "dynamic signature cracking",
            "bypass cloudflare",
            "evade ban",
            "ip pool",
            "account pool",
            "solve captcha automatically",
        )

        for subtype, artifact in cases.items():
            with self.subTest(subtype=subtype):
                diagnosis = classify_failure_artifact(artifact)
                public = enrich_for_users(diagnosis)
                combined = json.dumps(diagnosis, ensure_ascii=False).lower() + json.dumps(public, ensure_ascii=False).lower()

                self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
                self.assertEqual(diagnosis["subtype"], subtype)
                self.assertEqual(public["failure_layer"], "anti_bot_risk")
                self.assertTrue(public["safe_next_action"])
                for phrase in forbidden:
                    self.assertNotIn(phrase, combined)

    def test_failure_doctor_report_for_anti_bot_uses_compliance_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "input"
            out_dir = root / "report"
            input_dir.mkdir()
            (input_dir / "error.log").write_text(
                "HTTP 429 too many requests; verify you are human challenge page",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "diagnose", str(input_dir), "--out", str(out_dir)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            diagnosis = json.loads((out_dir / "diagnosis.json").read_text(encoding="utf-8"))
            prompt = (out_dir / "codex_fix_prompt.md").read_text(encoding="utf-8").lower()

            self.assertEqual(diagnosis["failure_layer"], "anti_bot_risk")
            self.assertIn("official api", prompt)
            self.assertIn("confirm authorization", prompt)
            self.assertNotIn("bypass cloudflare", prompt)
            self.assertNotIn("fingerprint spoofing", prompt)

    def test_corpus_v06_expands_to_150_cases(self):
        case_files = sorted((ROOT / "public_failure_corpus" / "cases").glob("*.yaml"))
        text = "\n".join(path.read_text(encoding="utf-8") for path in case_files)

        self.assertGreaterEqual(text.count("case_id:"), 150)
        self.assertGreaterEqual(text.count("likely_technical_category: website_change"), 25)
        self.assertGreaterEqual(text.count("likely_technical_category: anti_bot_risk"), 25)

    def test_v06_validation_ledger_has_actual_metrics(self):
        ledger = json.loads((ROOT / "validation" / "website_antibot_validation_50.json").read_text(encoding="utf-8"))
        summary = ledger["summary"]

        self.assertEqual(summary["sample_count"], 50)
        self.assertEqual(summary["website_change_cases"], 25)
        self.assertEqual(summary["anti_bot_risk_cases"], 25)
        self.assertEqual(summary["reasonable_classifications"], 50)
        self.assertEqual(summary["safe_next_actions"], 50)
        self.assertEqual(summary["forbidden_outputs"], 0)
        self.assertEqual(summary["severe_misclassifications"], 0)

        cases = ledger["cases"]
        self.assertEqual(len(cases), 50)
        self.assertTrue(all(item["codex_fix_prompt_generated"] for item in cases))
        self.assertTrue(all(not item["forbidden_output_hits"] for item in cases))

    def test_v06_validation_script_reproduces_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "website_antibot_validation_50.json"
            result = subprocess.run(
                [sys.executable, "scripts/validate_website_antibot.py", "--out", str(out_path)],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            generated = json.loads(out_path.read_text(encoding="utf-8"))
            summary = generated["summary"]
            self.assertEqual(summary["reasonable_classifications"], 50)
            self.assertEqual(summary["safe_next_actions"], 50)
            self.assertEqual(summary["forbidden_outputs"], 0)


if __name__ == "__main__":
    unittest.main()
