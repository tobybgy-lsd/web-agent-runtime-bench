from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AndroidPageObject:
    name: str
    locators: dict[str, dict[str, Any]]
