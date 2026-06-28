"""Built-in sanitized failure pack template helpers."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "examples" / "sanitized_failure_packs"


def list_templates(template_root: Path = TEMPLATE_ROOT) -> list[dict[str, str]]:
    if not template_root.exists():
        return []
    templates = []
    for case_dir in sorted(path for path in template_root.iterdir() if path.is_dir()):
        artifact_path = case_dir / "failure_artifact.json"
        if not artifact_path.exists():
            continue
        summary = _read_summary(case_dir / "README.md")
        templates.append(
            {
                "name": case_dir.name,
                "path": str(case_dir),
                "summary": summary,
            }
        )
    return templates


def copy_template(name: str, out_dir: Path | str, *, force: bool = False, template_root: Path = TEMPLATE_ROOT) -> Path:
    source = template_root / name
    if not source.exists() or not source.is_dir():
        available = ", ".join(item["name"] for item in list_templates(template_root)) or "none"
        raise FileNotFoundError(f"Template not found: {name}. Available templates: {available}")
    if not (source / "failure_artifact.json").exists():
        raise FileNotFoundError(f"Template is missing failure_artifact.json: {source}")

    destination = Path(out_dir)
    if destination.exists():
        if not force:
            raise FileExistsError(f"Output directory already exists: {destination}")
        if not destination.is_dir():
            raise FileExistsError(f"Output path exists and is not a directory: {destination}")
        shutil.rmtree(destination)

    shutil.copytree(source, destination)
    return destination


def _read_summary(readme_path: Path) -> str:
    if not readme_path.exists():
        return ""
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""
