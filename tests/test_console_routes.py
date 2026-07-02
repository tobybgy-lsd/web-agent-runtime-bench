from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from failure_doctor.console.server import create_console_app


class ConsoleRoutesTests(unittest.TestCase):
    def test_console_app_status_and_token_protected_import(self) -> None:
        with TemporaryDirectory() as tmp:
            app = create_console_app(workspace=Path(tmp) / "console", host="127.0.0.1", port=8765)

            status, headers, body = app.handle("GET", "/api/status", {}, b"")
            self.assertEqual(status, 200)
            self.assertTrue(headers["Content-Type"].startswith("application/json"))
            self.assertTrue(json.loads(body.decode("utf-8"))["local_only"])

            status, _headers, body = app.handle(
                "POST",
                "/api/import-report",
                {},
                json.dumps({"path": str(Path(tmp))}).encode("utf-8"),
            )
            self.assertEqual(status, 403)
            self.assertIn("token", body.decode("utf-8").lower())


    def test_console_index_uses_only_local_assets(self) -> None:
        with TemporaryDirectory() as tmp:
            app = create_console_app(workspace=Path(tmp) / "console", host="127.0.0.1", port=8765)

            status, _headers, body = app.handle("GET", "/", {}, b"")
            html = body.decode("utf-8")

            self.assertEqual(status, 200)
            self.assertIn("Agent Failure Doctor Console", html)
            self.assertNotIn("https://", html)
            self.assertNotIn("http://", html)
            self.assertIn("/static/console.css", html)
            self.assertIn("/static/console.js", html)


if __name__ == "__main__":
    unittest.main()

