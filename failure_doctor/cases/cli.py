from __future__ import annotations

import argparse
import json
from pathlib import Path

from .intake import create_public_case, export_public_case
from .issue_pack import create_issue_pack, validate_issue_pack
from .publish_check import publish_check_case
from .validation import validate_case


def add_case_parser(sub: argparse._SubParsersAction) -> None:
    case = sub.add_parser("case", help="Manage sanitized public-safe failure cases")
    case_sub = case.add_subparsers(dest="case_command")
    intake = case_sub.add_parser("intake", help="Sanitize a raw failure pack into a case")
    intake.add_argument("--input", required=True)
    intake.add_argument("--out", required=True)
    anonymize = case_sub.add_parser("anonymize", help="Anonymize a failure pack into a case")
    anonymize.add_argument("--input", required=True)
    anonymize.add_argument("--out", required=True)
    validate = case_sub.add_parser("validate", help="Validate a public case")
    validate.add_argument("--case", required=True)
    publish = case_sub.add_parser("publish-check", help="Check whether a case is safe to publish")
    publish.add_argument("--case", required=True)
    export = case_sub.add_parser("export-public", help="Export a publish-check-passing case")
    export.add_argument("--case", required=True)
    export.add_argument("--out", required=True)

    issue = sub.add_parser("issue-pack", help="Create or validate sanitized issue packs")
    issue_sub = issue.add_subparsers(dest="issue_pack_command")
    create = issue_sub.add_parser("create", help="Create a sanitized GitHub issue pack")
    create.add_argument("--input", required=True)
    create.add_argument("--out", required=True)
    issue_validate = issue_sub.add_parser("validate", help="Validate a sanitized issue pack")
    issue_validate.add_argument("issue_pack")


def handle_case(args: argparse.Namespace) -> int:
    command = getattr(args, "case_command", None)
    try:
        if command in {"intake", "anonymize"}:
            result = create_public_case(Path(args.input), Path(args.out))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["validation"]["status"] == "pass" else 3
        if command == "validate":
            result = validate_case(Path(args.case), Path(args.case) / "expected")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["status"] == "pass" else 3
        if command == "publish-check":
            result = publish_check_case(Path(args.case), Path(args.case) / "expected")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["status"] == "pass" else 3
        if command == "export-public":
            result = export_public_case(Path(args.case), Path(args.out))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("unknown case command")
    return 2


def handle_issue_pack(args: argparse.Namespace) -> int:
    command = getattr(args, "issue_pack_command", None)
    try:
        if command == "create":
            result = create_issue_pack(Path(args.input), Path(args.out))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["validation"]["status"] == "pass" else 3
        if command == "validate":
            result = validate_issue_pack(Path(args.issue_pack))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["status"] == "pass" else 3
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("unknown issue-pack command")
    return 2
