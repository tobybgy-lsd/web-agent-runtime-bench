from __future__ import annotations

from pathlib import Path

from .common import iter_text_files, lower_text, rel
from .models import SafetyFinding


CLOUD_MARKERS = ["browserbase", "stagehand", "remote_session", "remote trace", "provider_metadata", "remote browser"]
CLOUD_RISK_MARKERS = ["token", "secret", "customer", "unauthorized domain", "browser profile export", "raw cookies"]


def evaluate_cloud_artifact(root: Path | None) -> list[SafetyFinding]:
    if root is None or not root.exists():
        return []
    findings: list[SafetyFinding] = []
    for path in iter_text_files(root):
        text = lower_text(path)
        if not (any(marker in text for marker in CLOUD_MARKERS) or path.name.lower() in {"provider_metadata.json", "remote_session_log.json", "stagehand_run_log.json"}):
            continue
        hits = [pattern for pattern in CLOUD_RISK_MARKERS if pattern in text]
        if not hits:
            continue
        findings.append(
            SafetyFinding(
                id=f"finding_cloud_{len(findings)+1:03d}",
                type="cloud_artifact_risk",
                severity="high",
                evidence=[f"Offline cloud browser artifact risk in {rel(path, root)}: {', '.join(hits[:4])}"],
                affected_files=[rel(path, root)],
                decision="manual_review",
                safe_next_action="Review offline cloud browser artifacts locally; do not call provider APIs or upload raw artifacts during evaluation.",
                forbidden_actions=["cloud credential use", "remote browser control", "active probe"],
            )
        )
    return findings
