from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SCHEMA_VERSION = "safety_evaluation/v1"
TOOL_VERSION = "3.3.0"


@dataclass
class SafetyFinding:
    id: str
    type: str
    severity: str
    evidence: list[str]
    affected_files: list[str] = field(default_factory=list)
    decision: str = "warn"
    safe_next_action: str = "Manual review required before sharing or handing this artifact to an AI agent."
    forbidden_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "evidence": self.evidence,
            "affected_files": self.affected_files,
            "decision": self.decision,
            "safe_next_action": self.safe_next_action,
            "forbidden_actions": self.forbidden_actions,
        }
