from __future__ import annotations

from typing import TypedDict


class KbCase(TypedDict, total=False):
    case_id: str
    failure_type: str
    subtype: str
    fix_status: str
