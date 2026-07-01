import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SanitizeSharePackTests(unittest.TestCase):
    def run_doctor(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "failure_doctor", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sanitize_command_redacts_sensitive_logs_and_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            failed_run = Path(tmp) / "failed_run"
            failed_run.mkdir()
            (failed_run / "error.log").write_text(
                "\n".join(
                    [
                        "Authorization: Bearer secret-token-123",
                        "Cookie: sessionid=abc; csrftoken=def",
                        "api_key=sk-abcdefghijklmnop",
                        "email alice@example.com phone 13800138000 id 110101199003071234",
                        "customer 鐎殿喚濮崇粭?order ORD-20260629-0001",
                        "https://shop-real.example.com/internal/order/123",
                    ]
                ),
                encoding="utf-8",
            )
            (failed_run / "network.json").write_text(
                json.dumps(
                    [
                        {
                            "url": "https://internal.company.local/api/orders/ORD-20260629-0001",
                            "headers": {
                                "authorization": "Bearer network-secret",
                                "cookie": "sessionid=abc",
                            },
                            "postData": "phone=13800138000&email=alice@example.com",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            out_dir = Path(tmp) / "shareable_failure_pack"
            result = self.run_doctor("sanitize", str(failed_run), "--out", str(out_dir))

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            for name in [
                "sanitized_error.log",
                "sanitized_network.json",
                "redaction_report.json",
                "safe_to_share.json",
                "README_FOR_REVIEWER.md",
                "shareable_failure_pack.zip",
            ]:
                self.assertTrue((out_dir / name).exists(), name)

            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in out_dir.iterdir()
                if path.suffix in {".log", ".json", ".md"}
            )
            for raw_secret in [
                "secret-token-123",
                "sessionid=abc",
                "sk-abcdefghijklmnop",
                "alice@example.com",
                "13800138000",
                "110101199003071234",
                "customer_real_name",
                "ORD-20260629-0001",
                "internal.company.local",
                "shop-real.example.com/internal",
            ]:
                self.assertNotIn(raw_secret, combined)

            for placeholder in [
                "[REDACTED_AUTHORIZATION]",
                "[REDACTED_COOKIE]",
                "[REDACTED_API_KEY]",
                "[REDACTED_EMAIL]",
                "[REDACTED_PHONE]",
                "[REDACTED_ID]",
                "[REDACTED_CUSTOMER_NAME]",
                "[REDACTED_ORDER_ID]",
                "[REDACTED_INTERNAL_URL]",
            ]:
                self.assertIn(placeholder, combined)

            report = json.loads((out_dir / "redaction_report.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(report["total_redactions"], 9)
            self.assertIn("authorization", report["categories"])
            self.assertIn("cookie", report["categories"])
            self.assertIn("internal_url", report["categories"])

            safe_to_share = json.loads((out_dir / "safe_to_share.json").read_text(encoding="utf-8"))
            self.assertFalse(safe_to_share["safe_to_share"])
            self.assertIn("manual review", " ".join(safe_to_share["required_review"]).lower())

            with zipfile.ZipFile(out_dir / "shareable_failure_pack.zip") as archive:
                names = set(archive.namelist())
            self.assertIn("sanitized_error.log", names)
            self.assertIn("safe_to_share.json", names)

    def test_sanitize_trace_zip_writes_metadata_not_raw_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            failed_run = Path(tmp) / "failed_run"
            failed_run.mkdir()
            with zipfile.ZipFile(failed_run / "trace.zip", "w") as archive:
                archive.writestr("trace.trace", "raw trace should not be copied")

            out_dir = Path(tmp) / "shareable_failure_pack"
            result = self.run_doctor("sanitize", str(failed_run), "--out", str(out_dir))

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            metadata_path = out_dir / "sanitized_trace_metadata.json"
            self.assertTrue(metadata_path.exists())
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["trace_archives"][0]["filename"], "trace.zip")
            self.assertGreater(metadata["trace_archives"][0]["size_bytes"], 0)
            self.assertFalse((out_dir / "trace.zip").exists())
            with zipfile.ZipFile(out_dir / "shareable_failure_pack.zip") as archive:
                self.assertNotIn("trace.zip", set(archive.namelist()))

    def test_sanitize_refuses_to_write_output_over_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            failed_run = Path(tmp) / "failed_run"
            failed_run.mkdir()
            (failed_run / "error.log").write_text("page.goto timeout", encoding="utf-8")

            result = self.run_doctor("sanitize", str(failed_run), "--out", str(failed_run))

            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            self.assertIn("must not be the input path", result.stdout)
            self.assertTrue((failed_run / "error.log").exists())

    def test_docs_and_version_expose_v2_1_sanitize_share_pack(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn('version = "3.5.0"', pyproject)
        self.assertIn("## v2.1.0", changelog)
        self.assertIn("failure-doctor sanitize", readme)
        self.assertIn("Sanitize & Share Pack", readme)


if __name__ == "__main__":
    unittest.main()

