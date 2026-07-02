from __future__ import annotations

from typing import Any, Protocol


class ReasoningProvider(Protocol):
    def reason(self, bundle: dict[str, Any]) -> dict[str, Any]:
        ...
