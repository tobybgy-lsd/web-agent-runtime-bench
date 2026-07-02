from __future__ import annotations

from pathlib import Path

from .intake import create_public_case


def sanitize_case_input(input_path: Path, out: Path) -> dict:
    return create_public_case(input_path, out)
