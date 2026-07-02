from __future__ import annotations

from pathlib import Path
from typing import Any

from .ui_tree import parse_ui_tree_xml


def load_uiautomator_dump(path: Path | str) -> dict[str, Any]:
    return parse_ui_tree_xml(path)
