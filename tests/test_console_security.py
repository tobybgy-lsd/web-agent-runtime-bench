from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from failure_doctor.console.security import (
    ConsoleSecurityError,
    assert_host_allowed,
    safe_join,
    validate_local_token,
)


class ConsoleSecurityTests(unittest.TestCase):
    def test_console_rejects_lan_bind_without_explicit_flag(self) -> None:
        with self.assertRaises(ConsoleSecurityError):
            assert_host_allowed("0.0.0.0", allow_lan=False)


    def test_console_allows_lan_bind_only_with_flag(self) -> None:
        assert_host_allowed("0.0.0.0", allow_lan=True)


    def test_console_blocks_path_traversal(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()

            with self.assertRaises(ConsoleSecurityError):
                safe_join(workspace, "..", "outside.txt")


    def test_console_blocks_sensitive_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()

            with self.assertRaises(ConsoleSecurityError):
                safe_join(workspace, "raw_local_only_do_not_share", "cookie.json")


    def test_console_requires_local_token(self) -> None:
        self.assertTrue(validate_local_token("token-123", "token-123"))
        with self.assertRaises(ConsoleSecurityError):
            validate_local_token(None, "token-123")


if __name__ == "__main__":
    unittest.main()


