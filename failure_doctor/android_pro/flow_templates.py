from __future__ import annotations

from pathlib import Path


TEMPLATES = {
    "post_image_text_dry_run": "schema_version: android_flow/v1\nauthorized_target: true\ntarget_kind: mock_app\ndry_run_default: true\nallow_final_submit: false\nsteps:\n  - action: tap\n    text: add_image\n  - action: input\n    text: title\n  - action: tap\n    text: save_draft\n",
    "post_image_text_save_draft": "schema_version: android_flow/v1\nauthorized_target: true\ntarget_kind: mock_app\ndry_run_default: true\nallow_final_submit: false\nsteps:\n  - action: input\n    text: body\n  - action: tap\n    text: save_draft\n",
    "edit_sku_price_dry_run": "schema_version: android_flow/v1\nauthorized_target: true\ntarget_kind: mock_app\ndry_run_default: true\nallow_final_submit: false\nsteps:\n  - action: input\n    text: sku_price\n  - action: tap\n    text: save_draft\n",
    "fill_form_dry_run": "schema_version: android_flow/v1\nauthorized_target: true\ntarget_kind: mock_app\ndry_run_default: true\nallow_final_submit: false\nsteps:\n  - action: input\n    text: form_field\n  - action: verify\n    text: saved\n",
}


def scaffold_template(template: str, out: Path) -> dict:
    text = TEMPLATES.get(template)
    if text is None:
        raise ValueError(f"Unknown Android flow template: {template}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return {"schema_version": "android_flow_template/v1", "status": "pass", "template": template, "out": str(out)}
