"""Compatibility wrapper for the failure artifact classifier."""

from __future__ import annotations

from typing import Any, Mapping

from .classifier import classify_failure_artifact


def diagnose_artifact(artifact: Mapping[str, Any]) -> dict[str, Any]:
    return classify_failure_artifact(artifact)
