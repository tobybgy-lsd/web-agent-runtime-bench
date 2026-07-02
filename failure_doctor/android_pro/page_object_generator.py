from __future__ import annotations

from pathlib import Path

from .common import write_md
from .page_model import build_page_model


def generate_page_objects(ui_dump: Path, out: Path) -> dict:
    model = build_page_model(ui_dump, out, "detected_page")
    lines = [f"- Elements: {len(model['elements'])}"]
    for element in model["elements"]:
        lines.append(f"- `{element['element_id']}`: {element['recommended_locator']['strategy']} = `{element['recommended_locator']['value']}`")
    write_md(out / "page_object_summary.md", "Android Page Object Summary", lines)
    return {"schema_version": "android_page_object_generation/v1", "status": "pass", "pages": [model], "page_count": 1}
