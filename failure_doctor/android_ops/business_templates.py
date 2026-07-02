from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .ops_audit import write_json


TEMPLATE_TYPES = [
    "post_image_text_save_draft",
    "post_image_text_dry_run",
    "edit_product_title_dry_run",
    "edit_sku_price_dry_run",
    "edit_inventory_dry_run",
    "upload_images_dry_run",
    "fill_business_form_dry_run",
    "batch_save_drafts",
    "media_picker_business_mock",
    "permission_dialog_business_mock",
]


def template_payload(template_type: str) -> dict[str, Any]:
    if template_type not in TEMPLATE_TYPES:
        raise ValueError(f"unknown Android business template: {template_type}")
    steps = [
        {"action": "open_mock_app", "locator": {"resource_id": "com.example:id/root"}},
        {"action": "fill_text", "field": "title", "dry_run": True},
        {"action": "save_draft", "locator": {"resource_id": "com.example:id/save_draft"}},
    ]
    if "sku" in template_type:
        steps.append({"action": "preview_sku_price_change", "dry_run": True})
    if "inventory" in template_type:
        steps.append({"action": "preview_inventory_change", "dry_run": True})
    return {
        "schema_version": "android_business_template/v1",
        "flow_id": template_type,
        "authorized_target": True,
        "target_kind": "mock_app",
        "dry_run_default": True,
        "allow_final_submit": False,
        "allow_business_mutation": False,
        "no_external_upload": True,
        "mode": "dry_run",
        "steps": steps,
    }


def list_templates() -> dict[str, Any]:
    return {
        "schema_version": "android_business_template_list/v1",
        "templates": TEMPLATE_TYPES,
        "all_dry_run_by_default": True,
        "final_submit_blocked_by_default": True,
        "business_mutation_blocked_by_default": True,
    }


def scaffold_template(template_type: str, out: Path) -> dict[str, Any]:
    payload = template_payload(template_type)
    _write_yaml_like(out, payload)
    return payload


def install_template_files(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for name in TEMPLATE_TYPES:
        _write_yaml_like(root / f"{name}.yml", template_payload(name))


def copy_gallery(source: Path, out: Path) -> dict[str, Any]:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(source, out)
    return write_json(out / "gallery_manifest.json", {"schema_version": "android_ops_gallery/v1", "status": "pass"})


def _write_yaml_like(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "schema_version: android_business_template/v1",
        f"flow_id: {payload['flow_id']}",
        "authorized_target: true",
        "target_kind: mock_app",
        "dry_run_default: true",
        "allow_final_submit: false",
        "allow_business_mutation: false",
        "no_external_upload: true",
        "steps:",
    ]
    for step in payload["steps"]:
        lines.append(f"  - action: {step['action']}")
        if "field" in step:
            lines.append(f"    field: {step['field']}")
        if "dry_run" in step:
            lines.append("    dry_run: true")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

