from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .inspector import write_inspection
from .registry import disable_plugin, enable_plugin, init_workspace, install_plugin, read_registry
from .runner import run_plugin
from .scaffold import scaffold_plugin
from .validator import validate_plugin


def add_plugin_parser(sub: argparse._SubParsersAction) -> None:
    plugin = sub.add_parser("plugin", help="Manage local-only Agent Failure Doctor plugins")
    plugin_sub = plugin.add_subparsers(dest="plugin_command")

    plugin_sub.add_parser("list", help="List installed plugins").add_argument(
        "--workspace", default=".failure-doctor-plugins", help="Plugin workspace"
    )

    scaffold = plugin_sub.add_parser("scaffold", help="Create a local-only plugin scaffold")
    scaffold.add_argument("--type", required=True, dest="plugin_type")
    scaffold.add_argument("--name", required=True)
    scaffold.add_argument("--out", required=True)

    validate = plugin_sub.add_parser("validate", help="Validate a plugin manifest and safety boundary")
    validate.add_argument("plugin_dir")

    inspect = plugin_sub.add_parser("inspect", help="Inspect plugin metadata and validation state")
    inspect.add_argument("plugin_dir")

    install = plugin_sub.add_parser("install", help="Install a validation-passed plugin into a workspace")
    install.add_argument("plugin_dir")
    install.add_argument("--workspace", default=".failure-doctor-plugins")

    enable = plugin_sub.add_parser("enable", help="Enable an installed validation-passed plugin")
    enable.add_argument("plugin_id")
    enable.add_argument("--workspace", default=".failure-doctor-plugins")

    disable = plugin_sub.add_parser("disable", help="Disable an installed plugin")
    disable.add_argument("plugin_id")
    disable.add_argument("--workspace", default=".failure-doctor-plugins")

    run = plugin_sub.add_parser("run", help="Run a safe local plugin and emit candidate output")
    run.add_argument("plugin_id")
    run.add_argument("--workspace", default=".failure-doctor-plugins")
    run.add_argument("--input", required=True)
    run.add_argument("--out", required=True)

    export = plugin_sub.add_parser("export", help="Export sanitized plugin metadata")
    export.add_argument("plugin_id")
    export.add_argument("--workspace", default=".failure-doctor-plugins")
    export.add_argument("--out", required=True)
    export.add_argument("--sanitized-only", action="store_true")

    audit = plugin_sub.add_parser("audit", help="Show plugin workspace audit log")
    audit.add_argument("--workspace", default=".failure-doctor-plugins")


def handle_plugin(args: argparse.Namespace) -> int:
    command = getattr(args, "plugin_command", None)
    try:
        if command == "list":
            registry = read_registry(Path(args.workspace))
            print(json.dumps(registry, indent=2, ensure_ascii=False))
            return 0
        if command == "scaffold":
            result = scaffold_plugin(str(args.plugin_type), str(args.name), Path(args.out))
            print("Agent Failure Doctor Plugin Scaffold")
            print(f"Plugin: {result['plugin_id']}")
            print(f"Output: {result['path']}")
            return 0
        if command == "validate":
            report = validate_plugin(Path(args.plugin_dir))
            print("Agent Failure Doctor Plugin Validation")
            print(f"Status: {report.get('status')}")
            print(f"Risk: {report.get('risk_level')}")
            print(f"Output: {Path(args.plugin_dir) / 'plugin_validation_report.json'}")
            return 0 if report.get("status") == "pass" else 3
        if command == "inspect":
            payload = write_inspection(Path(args.plugin_dir))
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0
        if command == "install":
            result = install_plugin(Path(args.plugin_dir), Path(args.workspace))
            print("Agent Failure Doctor Plugin Install")
            print(f"Plugin: {result['plugin_id']}")
            print(f"Workspace: {result['workspace']}")
            return 0
        if command == "enable":
            result = enable_plugin(str(args.plugin_id), Path(args.workspace))
            print(f"Plugin {result['plugin_id']} enabled")
            return 0
        if command == "disable":
            result = disable_plugin(str(args.plugin_id), Path(args.workspace))
            print(f"Plugin {result['plugin_id']} disabled")
            return 0
        if command == "run":
            result = run_plugin(
                str(args.plugin_id),
                workspace=Path(args.workspace),
                input_dir=Path(args.input),
                out_dir=Path(args.out),
            )
            print("Agent Failure Doctor Plugin Run")
            print(f"Plugin: {result.get('plugin_id')}")
            print(f"Output: {args.out}")
            return 0
        if command == "export":
            out = Path(args.out)
            out.mkdir(parents=True, exist_ok=True)
            plugin_dir = Path(args.workspace) / "installed" / str(args.plugin_id)
            if not plugin_dir.exists():
                raise FileNotFoundError(f"plugin not installed: {args.plugin_id}")
            for name in ("plugin_manifest.json", "plugin_validation_report.json", "README.md", "FORBIDDEN_ACTIONS.md"):
                src = plugin_dir / name
                if src.exists():
                    shutil.copy2(src, out / name)
            print("Agent Failure Doctor Plugin Export")
            print(f"Output: {out}")
            return 0
        if command == "audit":
            workspace = init_workspace(Path(args.workspace))
            audit_path = workspace / "audit_log.jsonl"
            print(audit_path.read_text(encoding="utf-8") if audit_path.exists() else "")
            return 0
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(str(exc))
        return 2
    print("unknown plugin command")
    return 2
