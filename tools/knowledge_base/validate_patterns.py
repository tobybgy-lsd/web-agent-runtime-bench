from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from tools.knowledge_base.load_patterns import load_patterns, pattern_text


REQUIRED_FIELDS = (
    "id",
    "version",
    "applies_to",
    "failure_layer",
    "technical_category",
    "subtype",
    "evidence_patterns",
    "positive_evidence",
    "negative_evidence",
    "fix_plan",
    "verification",
    "safety",
)
SECRET_RE = re.compile(r"(sk-[A-Za-z0-9]{12,}|authorization:\s*bearer|cookie:\s*[^,\s]+)", re.I)
FORBIDDEN_RE = re.compile(
    r"(captcha bypass|bot evasion|fingerprint spoofing|dynamic signature cracking|"
    r"cloudflare bypass|akamai bypass|datadome bypass|perimeterx bypass|"
    r"ip pool|account pool|ban evasion)",
    re.I,
)


def validate_pattern(pattern: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in pattern:
            errors.append(f"{pattern.get('id', '<missing-id>')}: missing {field}")
    safety = pattern.get("safety", {})
    if not isinstance(safety, dict):
        errors.append(f"{pattern.get('id')}: safety must be object")
    elif safety.get("anti_bot") and not safety.get("forbidden_actions"):
        errors.append(f"{pattern.get('id')}: anti_bot patterns must declare forbidden_actions")
    text = pattern_text(pattern)
    if SECRET_RE.search(text):
        errors.append(f"{pattern.get('id')}: possible secret or credential")
    if FORBIDDEN_RE.search(text):
        errors.append(f"{pattern.get('id')}: forbidden bypass language")
    return errors


def main() -> int:
    patterns = load_patterns()
    errors: list[str] = []
    for pattern in patterns:
        errors.extend(validate_pattern(pattern))
    by_layer = Counter(str(pattern.get("failure_layer")) for pattern in patterns)
    anti_bot_patterns = sum(1 for pattern in patterns if pattern.get("safety", {}).get("anti_bot"))
    payload = {
        "schema_version": "knowledge_base_validation/v1",
        "total_patterns": len(patterns),
        "anti_bot_patterns": anti_bot_patterns,
        "patterns_by_layer": dict(sorted(by_layer.items())),
        "forbidden_output_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not errors and len(patterns) >= 120 else 1


if __name__ == "__main__":
    raise SystemExit(main())
