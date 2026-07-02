from __future__ import annotations

import argparse
import json
from pathlib import Path

from .store import KnowledgeBase, render_matches_md, render_recommendations_md


def add_kb_parser(sub) -> None:
    kb = sub.add_parser("kb", help="Manage the local-only failure knowledge base")
    kb_sub = kb.add_subparsers(dest="kb_command", required=True)

    init = kb_sub.add_parser("init", help="Initialize a local failure knowledge base")
    init.add_argument("--path", required=True)

    status = kb_sub.add_parser("status", help="Show KB health")
    status.add_argument("--kb", required=True)

    import_report = kb_sub.add_parser("import-report", help="Import a sanitized report")
    import_report.add_argument("--kb", required=True)
    import_report.add_argument("--report", required=True)
    import_report.add_argument("--sanitized-only", action="store_true")

    import_batch = kb_sub.add_parser("import-batch", help="Import reports from a batch report")
    import_batch.add_argument("--kb", required=True)
    import_batch.add_argument("--batch-report", required=True)

    import_ci = kb_sub.add_parser("import-ci", help="Import a sanitized CI report")
    import_ci.add_argument("--kb", required=True)
    import_ci.add_argument("--ci-report", required=True)

    search = kb_sub.add_parser("search", help="Search local similar failures")
    search.add_argument("--kb", required=True)
    search.add_argument("--query", required=True)

    match = kb_sub.add_parser("match", help="Match a report against local historical cases")
    match.add_argument("--kb", required=True)
    match.add_argument("--report", required=True)
    match.add_argument("--out", required=True)

    list_cmd = kb_sub.add_parser("list", help="List KB cases")
    list_cmd.add_argument("--kb", required=True)

    show = kb_sub.add_parser("show", help="Show a KB case")
    show.add_argument("--kb", required=True)
    show.add_argument("--case-id", required=True)

    promote = kb_sub.add_parser("promote-fix", help="Promote a verified fix from a verification report")
    promote.add_argument("--kb", required=True)
    promote.add_argument("--case-id", required=True)
    promote.add_argument("--verification", required=True)

    mark = kb_sub.add_parser("mark-regression", help="Mark a case as a regression case")
    mark.add_argument("--kb", required=True)
    mark.add_argument("--case-id", required=True)

    export = kb_sub.add_parser("export", help="Export a sanitized KB package")
    export.add_argument("--kb", required=True)
    export.add_argument("--out", required=True)
    export.add_argument("--sanitized-only", action="store_true")

    validate = kb_sub.add_parser("validate", help="Validate KB health")
    validate.add_argument("--kb", required=True)

    rebuild = kb_sub.add_parser("rebuild-index", help="Rebuild local KB indexes")
    rebuild.add_argument("--kb", required=True)


def handle_kb(args: argparse.Namespace) -> int:
    command = args.kb_command
    try:
        if command == "init":
            manifest = KnowledgeBase(Path(args.path)).init()
            print("Agent Failure Doctor Local KB")
            print(f"Initialized: {args.path}")
            print(f"Schema: {manifest['schema_version']}")
            return 0
        kb = KnowledgeBase(Path(args.kb))
        if command == "status" or command == "validate":
            result = kb.status()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result.get("status") == "pass" else 3
        if command == "import-report":
            case = kb.import_report(Path(args.report))
            print(f"Imported {case['case_id']}")
            return 0
        if command == "import-batch":
            cases = kb.import_batch(Path(args.batch_report))
            print(f"Imported {len(cases)} reports")
            return 0
        if command == "import-ci":
            case = kb.import_ci(Path(args.ci_report))
            print(f"Imported {case['case_id']}")
            return 0
        if command == "search":
            rows = kb.search(str(args.query))
            print(json.dumps({"results": rows}, indent=2, ensure_ascii=False))
            return 0
        if command == "match":
            result = kb.match_report(Path(args.report), Path(args.out))
            print(json.dumps({"matches": result["matches"]}, indent=2, ensure_ascii=False))
            return 0
        if command == "list":
            print(json.dumps({"cases": kb.list_cases()}, indent=2, ensure_ascii=False))
            return 0
        if command == "show":
            print(json.dumps(kb.get_case(str(args.case_id)), indent=2, ensure_ascii=False))
            return 0
        if command == "promote-fix":
            fix = kb.promote_fix(str(args.case_id), Path(args.verification))
            print(json.dumps(fix, indent=2, ensure_ascii=False))
            return 0
        if command == "mark-regression":
            case = kb.mark_regression(str(args.case_id))
            print(json.dumps(case, indent=2, ensure_ascii=False))
            return 0
        if command == "export":
            result = kb.export_sanitized(Path(args.out))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        if command == "rebuild-index":
            result = kb.rebuild_indexes()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("unknown kb command")
    return 2
