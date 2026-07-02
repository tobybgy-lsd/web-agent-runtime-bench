from __future__ import annotations

import hashlib
import re
from typing import Any

from .redaction import stable_text


def normalize_tokens(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"https?://\S+", " url ", text)
    text = re.sub(r"[a-f0-9]{16,}", " hex ", text)
    text = re.sub(r"\b\d+\b", " num ", text)
    words = re.findall(r"[a-z_][a-z0-9_\-]{2,}", text)
    stop = {"the", "and", "with", "from", "this", "that", "after", "before"}
    return [word for word in words if word not in stop][:80]


def short_hash(parts: list[str]) -> str:
    data = "|".join(parts)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]


def fingerprint_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("raw_diagnosis") if isinstance(payload.get("raw_diagnosis"), dict) else payload
    failure_type = str(payload.get("failure_type") or payload.get("technical_category") or raw.get("failure_type") or "unknown")
    subtype = str(payload.get("subtype") or raw.get("subtype") or "unknown")
    framework = str(payload.get("framework") or raw.get("framework") or "unknown")
    domain = str(payload.get("domain") or raw.get("domain") or "generic")
    observations = raw.get("observations") if isinstance(raw.get("observations"), dict) else {}
    text = stable_text({"payload": payload, "observations": observations})
    tokens = normalize_tokens(text)
    primary = short_hash([failure_type, subtype, framework, *tokens[:12]])
    context = short_hash([domain, framework, *tokens[12:28]])
    return {
        "failure_type": failure_type,
        "subtype": subtype,
        "framework": framework,
        "domain": domain,
        "error_signature": " ".join(tokens[:16]),
        "network_status_signature": _pick(tokens, ("401", "403", "404", "429", "500", "proxy", "dns", "tls")),
        "trace_action_signature": _pick(tokens, ("click", "goto", "locator", "route", "storage")),
        "dom_signature": _pick(tokens, ("selector", "shadow", "dom", "iframe")),
        "visual_signature": _pick(tokens, ("overlay", "screenshot", "viewport", "ocr")),
        "ocr_signature": _pick(tokens, ("ocr", "document", "text")),
        "data_quality_signature": _pick(tokens, ("schema", "duplicate", "checkpoint", "pagination")),
        "safety_signature": _pick(tokens, ("anti_bot", "fingerprint", "captcha", "authorization")),
        "regulated_signature": _pick(tokens, ("finance", "healthcare", "government", "audit")),
        "primary_fingerprint": primary,
        "secondary_fingerprints": [short_hash([failure_type, subtype]), short_hash(tokens[:24])],
        "normalized_error_signature": " ".join(tokens[:32]),
        "normalized_evidence_signature": short_hash(tokens[:48]),
        "context_signature": context,
        "tokens": tokens,
    }


def _pick(tokens: list[str], needles: tuple[str, ...]) -> str:
    hits = [token for token in tokens if any(needle in token for needle in needles)]
    return " ".join(hits[:8])
