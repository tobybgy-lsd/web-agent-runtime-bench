from __future__ import annotations

import argparse
import json
from pathlib import Path

from .approvals import create_request, decide_request
from .audit import export_audit
from .permissions import list_roles
from .policy import list_policies, set_policy
from .users import add_user, disable_user, list_users
from .workspace import init_workspace, validate_workspace


def add_enterprise_parser(sub) -> None:
    enterprise = sub.add_parser("enterprise", help="Manage local enterprise governance")
    ent_sub = enterprise.add_subparsers(dest="enterprise_command", required=True)

    init = ent_sub.add_parser("init", help="Initialize a local enterprise workspace")
    init.add_argument("--workspace", required=True)

    status = ent_sub.add_parser("status", help="Show enterprise workspace status")
    status.add_argument("--workspace", required=True)
    validate = ent_sub.add_parser("validate", help="Validate enterprise workspace")
    validate.add_argument("--workspace", required=True)

    user = ent_sub.add_parser("user", help="Manage local users")
    user_sub = user.add_subparsers(dest="user_command", required=True)
    user_add = user_sub.add_parser("add")
    user_add.add_argument("--workspace", required=True)
    user_add.add_argument("--username", required=True)
    user_add.add_argument("--role", required=True)
    user_disable = user_sub.add_parser("disable")
    user_disable.add_argument("--workspace", required=True)
    user_disable.add_argument("--username", required=True)
    user_list = user_sub.add_parser("list")
    user_list.add_argument("--workspace", required=True)

    role = ent_sub.add_parser("role", help="Manage roles")
    role_sub = role.add_subparsers(dest="role_command", required=True)
    role_list = role_sub.add_parser("list")
    role_list.add_argument("--workspace", required=True)
    role_show = role_sub.add_parser("show")
    role_show.add_argument("--workspace", required=True)
    role_show.add_argument("--role", required=True)

    policy = ent_sub.add_parser("policy", help="Manage enterprise policy")
    policy_sub = policy.add_subparsers(dest="policy_command", required=True)
    policy_list = policy_sub.add_parser("list")
    policy_list.add_argument("--workspace", required=True)
    policy_set = policy_sub.add_parser("set")
    policy_set.add_argument("--workspace", required=True)
    policy_set.add_argument("--policy", required=True)

    request = ent_sub.add_parser("request", help="Create approval requests")
    request_sub = request.add_subparsers(dest="request_command", required=True)
    for name in ("export", "handoff", "raw-access"):
        req = request_sub.add_parser(name)
        req.add_argument("--workspace", required=True)
        req.add_argument("--report", required=True)
        req.add_argument("--kind", default="share_pack")
        req.add_argument("--target", default="")
        req.add_argument("--reason", default="")

    approve = ent_sub.add_parser("approve", help="Approve or reject a pending request")
    approve.add_argument("--workspace", required=True)
    approve.add_argument("--request-id", required=True)
    approve.add_argument("--decision", required=True, choices=["approve", "reject"])
    approve.add_argument("--reason", default="")

    audit = ent_sub.add_parser("audit", help="Audit ledger operations")
    audit_sub = audit.add_subparsers(dest="audit_command", required=True)
    audit_export = audit_sub.add_parser("export")
    audit_export.add_argument("--workspace", required=True)
    audit_export.add_argument("--out", required=True)
    audit_export.add_argument("--sanitized-only", action="store_true")
    audit_query = audit_sub.add_parser("query")
    audit_query.add_argument("--workspace", required=True)
    audit_query.add_argument("--actor", default=None)
    audit_query.add_argument("--since", default=None)

    report = ent_sub.add_parser("report", help="Write enterprise report")
    report.add_argument("--workspace", required=True)
    report.add_argument("--out", required=True)


def handle_enterprise(args: argparse.Namespace) -> int:
    try:
        command = args.enterprise_command
        workspace = Path(getattr(args, "workspace", ".failure-doctor-enterprise"))
        if command == "init":
            _print(init_workspace(workspace))
            return 0
        if command in {"status", "validate"}:
            result = validate_workspace(workspace)
            _print(result)
            return 0 if result.get("status") == "pass" else 3
        if command == "user":
            if args.user_command == "add":
                _print(add_user(workspace, args.username, args.role))
                return 0
            if args.user_command == "disable":
                _print(disable_user(workspace, args.username))
                return 0
            if args.user_command == "list":
                _print(list_users(workspace))
                return 0
        if command == "role":
            roles = list_roles()
            if args.role_command == "show":
                roles = [role for role in roles if role["role"] == args.role]
            _print({"roles": roles})
            return 0
        if command == "policy":
            if args.policy_command == "list":
                _print(list_policies(workspace))
                return 0
            _print(set_policy(workspace, Path(args.policy)))
            return 0
        if command == "request":
            request_type = {
                "export": f"{args.kind}_export",
                "handoff": "handoff_export",
                "raw-access": "raw_access",
            }[args.request_command]
            _print(create_request(workspace, request_type, args.report))
            return 0
        if command == "approve":
            _print(decide_request(workspace, args.request_id, args.decision, args.reason))
            return 0
        if command == "audit":
            if args.audit_command == "export":
                _print(export_audit(workspace, Path(args.out), sanitized_only=bool(args.sanitized_only)))
                return 0
            _print({"status": "pass", "query": "audit query is local-only", "actor": args.actor})
            return 0
        if command == "report":
            out = Path(args.out)
            out.mkdir(parents=True, exist_ok=True)
            result = validate_workspace(workspace)
            (out / "enterprise_report.json").write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            _print(result)
            return 0
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 2
    print("unknown enterprise command")
    return 2


def _print(payload: object) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
