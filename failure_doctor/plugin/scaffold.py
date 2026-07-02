from __future__ import annotations

import json
import re
from pathlib import Path

from .manifest import write_manifest
from .models import DEFAULT_HOOKS_BY_TYPE, PLUGIN_SCHEMA_VERSION, PLUGIN_TYPES, SAFE_DEFAULT_PERMISSIONS


def normalize_plugin_id(name: str) -> str:
    plugin_id = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip()).strip("_").lower()
    if not plugin_id or not re.match(r"^[a-z][a-z0-9_]*$", plugin_id):
        raise ValueError("plugin name must start with a letter and contain only letters, numbers, and underscores")
    return plugin_id


def scaffold_plugin(plugin_type: str, name: str, out: Path) -> dict:
    if plugin_type not in PLUGIN_TYPES:
        raise ValueError(f"unsupported plugin type: {plugin_type}")
    plugin_id = normalize_plugin_id(name)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    schemas = out / "schemas"
    tests = out / "tests"
    schemas.mkdir(exist_ok=True)
    tests.mkdir(exist_ok=True)
    manifest = {
        "schema_version": PLUGIN_SCHEMA_VERSION,
        "plugin_id": plugin_id,
        "name": plugin_id.replace("_", " ").title(),
        "version": "0.1.0",
        "type": plugin_type,
        "entrypoint": "plugin.py",
        "description": f"Local-only {plugin_type} plugin for Agent Failure Doctor.",
        "author": "local",
        "license": "MIT",
        "local_only": True,
        "no_upload": True,
        "no_external_api": True,
        "requires_network": False,
        "requires_shell": False,
        "requires_write_access": False,
        "permissions": sorted(SAFE_DEFAULT_PERMISSIONS),
        "hooks": DEFAULT_HOOKS_BY_TYPE[plugin_type],
        "schemas": {
            "input": "schemas/input.schema.json",
            "output": "schemas/output.schema.json",
        },
        "safety": {
            "forbidden_actions_declared": True,
            "raw_secret_handling": "redact",
            "private_solution_allowed": False,
            "bypass_guidance_allowed": False,
        },
    }
    write_manifest(out, manifest)
    (out / "plugin.py").write_text(_plugin_py(plugin_id, plugin_type), encoding="utf-8")
    (schemas / "input.schema.json").write_text(_schema("input"), encoding="utf-8")
    (schemas / "output.schema.json").write_text(_schema("output"), encoding="utf-8")
    (tests / "test_plugin.py").write_text(_test_plugin(plugin_id), encoding="utf-8")
    (out / "README.md").write_text(_readme(plugin_id, plugin_type), encoding="utf-8")
    (out / "FORBIDDEN_ACTIONS.md").write_text(_forbidden_actions(), encoding="utf-8")
    return {"plugin_id": plugin_id, "type": plugin_type, "path": str(out)}


def _schema(kind: str) -> str:
    return json.dumps(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": f"Agent Failure Doctor Plugin {kind.title()}",
            "type": "object",
            "additionalProperties": True,
        },
        indent=2,
    ) + "\n"


def _plugin_py(plugin_id: str, plugin_type: str) -> str:
    return f'''"""Local-only Agent Failure Doctor plugin scaffold.

This scaffold returns extension candidates only. The core validator remains the
final authority.
"""

PLUGIN_ID = "{plugin_id}"
PLUGIN_TYPE = "{plugin_type}"


def run(input_dir, out_dir, context=None):
    return {{
        "schema_version": "failure_doctor_plugin_result/v1",
        "plugin_id": PLUGIN_ID,
        "plugin_type": PLUGIN_TYPE,
        "status": "pass",
        "evidence_items": [
            {{
                "id": f"{{PLUGIN_ID}}-evidence-001",
                "kind": "plugin_summary",
                "summary": "Synthetic local-only plugin evidence candidate.",
            }}
        ],
        "diagnosis_candidates": [
            {{
                "plugin_id": PLUGIN_ID,
                "failure_type": "plugin_candidate",
                "subtype": f"{{PLUGIN_ID}}_candidate",
                "confidence": 0.5,
                "risk_note": "Candidate only; core diagnosis remains final authority.",
            }}
        ],
    }}
'''


def _test_plugin(plugin_id: str) -> str:
    return f'''from pathlib import Path

import plugin


def test_plugin_returns_schema():
    result = plugin.run(Path("."), Path("."))
    assert result["plugin_id"] == "{plugin_id}"
    assert result["schema_version"] == "failure_doctor_plugin_result/v1"
'''


def _readme(plugin_id: str, plugin_type: str) -> str:
    return f"""# {plugin_id}

Local-only Agent Failure Doctor `{plugin_type}` plugin.

This plugin is disabled by default, requires manifest validation, and emits
candidates only. Core safety gates and validators remain final authority.
"""


def _forbidden_actions() -> str:
    return """# Forbidden Actions

No CAPTCHA bypass.
No anti-bot evasion.
No fingerprint spoofing.
No signature cracking.
No credential extraction.
No browser profile reading.
No raw secret export.
No external upload by default.
No private answer content.
"""
