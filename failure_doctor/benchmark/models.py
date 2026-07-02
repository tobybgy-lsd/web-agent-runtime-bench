from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


BENCHMARK_SCHEMA_VERSION = "failure_doctor_benchmark/v1"
SUPPORTED_SUITES = {"public-safe", "regression"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def synthetic_case(case_id: str, suite: str, index: int) -> dict[str, Any]:
    failure_type = [
        "playwright_locator_failure",
        "network_proxy_dns_tls",
        "playwright_storage_state_context",
        "website_change",
        "anti_bot_risk",
        "visual_runtime_failure",
        "ocr_document_evidence",
        "data_engineering_failure",
    ][index % 8]
    subtype = f"{failure_type}_public_safe_{index % 5}"
    return {
        "schema_version": "public_case/v1",
        "case_id": case_id,
        "suite": suite,
        "source": "synthetic",
        "public_safe": True,
        "sanitized": True,
        "contains_real_secret": False,
        "contains_private_solution": False,
        "contains_customer_data": False,
        "contains_pii": False,
        "contains_phi": False,
        "contains_credentials": False,
        "diagnosis_only_no_bypass": True,
        "license": "MIT",
        "failure_type": failure_type,
        "subtype": subtype,
        "framework": "generic",
    }
