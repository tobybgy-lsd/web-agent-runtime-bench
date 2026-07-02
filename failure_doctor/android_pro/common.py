from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import ANDROID_PRO_VERSION

FORBIDDEN_TERMS = [
    "captcha " + "bypass",
    "anti-bot " + "evasion",
    "fingerprint " + "spoofing",
    "dynamic signature " + "cracking",
    "frida",
    "xposed",
    "magisk",
    "root bypass",
    "ssl pinning " + "bypass",
    "apk crack",
    "apk re-sign",
    "account " + "pool",
    "ip " + "pool",
]

FINAL_ACTION_TERMS = ["发布", "提交", "确认", "付款", "下单", "交易", "发送", "publish", "submit", "pay", "order", "confirm"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [f"# {title}", ""] + lines
    path.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    if path.is_dir():
        for name in ("flow.yml", "flow.yaml", "ui.xml", "android_app_profile.json", "android_locator_registry.json"):
            candidate = path / name
            if candidate.exists():
                return candidate.read_text(encoding="utf-8", errors="ignore")
        return "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in path.glob("*") if p.is_file())
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    steps: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_steps = False
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "steps:":
            in_steps = True
            continue
        if in_steps and stripped.startswith("- "):
            current = {}
            steps.append(current)
            item = stripped[2:].strip()
            if ":" in item:
                key, value = item.split(":", 1)
                current[key.strip()] = parse_scalar(value.strip())
            continue
        if in_steps and current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = parse_scalar(value.strip())
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            data[key.strip()] = parse_scalar(value.strip())
    if steps:
        data["steps"] = steps
    return data


def parse_scalar(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() in {"null", "none", ""}:
        return None if value.lower() in {"null", "none"} else ""
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def read_flow(path: Path) -> dict[str, Any]:
    text = load_text(path)
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return parse_simple_yaml(text)


def parse_ui_nodes(path: Path) -> list[dict[str, Any]]:
    text = load_text(path)
    root = ET.fromstring(text)
    nodes: list[dict[str, Any]] = []
    for idx, node in enumerate(root.iter("node")):
        attrs = node.attrib
        nodes.append(
            {
                "index": idx,
                "resource_id": attrs.get("resource-id", ""),
                "text": attrs.get("text", ""),
                "content_desc": attrs.get("content-desc", ""),
                "class_name": attrs.get("class", ""),
                "bounds": attrs.get("bounds", ""),
                "clickable": attrs.get("clickable", ""),
                "enabled": attrs.get("enabled", ""),
            }
        )
    return nodes


def node_role(node: dict[str, Any]) -> str:
    class_name = str(node.get("class_name", "")).lower()
    text = str(node.get("text", "")).lower()
    if "edittext" in class_name:
        return "input"
    if "button" in class_name or "btn" in str(node.get("resource_id", "")).lower() or text in {"save", "publish", "submit"}:
        return "button"
    if "image" in class_name:
        return "image"
    if "webview" in class_name:
        return "webview"
    return "element"


def locator_for_node(node: dict[str, Any]) -> dict[str, str]:
    if node.get("resource_id"):
        return {"strategy": "resource_id", "value": str(node["resource_id"])}
    if node.get("content_desc"):
        return {"strategy": "accessibility_id", "value": str(node["content_desc"])}
    if node.get("text"):
        return {"strategy": "text", "value": str(node["text"])}
    return {"strategy": "class_hierarchy", "value": f"{node.get('class_name', 'node')}[{node.get('index', 0)}]"}


def has_forbidden_text(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in FORBIDDEN_TERMS if term in lower]


def is_final_action_text(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in FINAL_ACTION_TERMS)
