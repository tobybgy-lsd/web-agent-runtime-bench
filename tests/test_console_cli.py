from __future__ import annotations

import unittest

from failure_doctor.cli import build_parser


class ConsoleCliTests(unittest.TestCase):
    def test_console_cli_defaults_are_local_only(self) -> None:
        args = build_parser().parse_args(["console"])

        self.assertEqual(args.command, "console")
        self.assertEqual(args.host, "127.0.0.1")
        self.assertEqual(args.port, 8765)
        self.assertEqual(args.workspace, ".failure-doctor-console")
        self.assertFalse(args.open)
        self.assertFalse(args.allow_lan)
        self.assertFalse(args.readonly)

    def test_console_cli_accepts_explicit_workspace_and_import(self) -> None:
        args = build_parser().parse_args(
            [
                "console",
                "--host",
                "127.0.0.1",
                "--port",
                "9876",
                "--workspace",
                "console-work",
                "--readonly",
                "--no-browser",
                "--import-report",
                "report",
                "--import-batch",
                "batch",
            ]
        )

        self.assertEqual(args.port, 9876)
        self.assertEqual(args.workspace, "console-work")
        self.assertTrue(args.readonly)
        self.assertTrue(args.no_browser)
        self.assertEqual(args.import_report, "report")
        self.assertEqual(args.import_batch, "batch")


if __name__ == "__main__":
    unittest.main()

