from __future__ import annotations

from pathlib import Path
from typing import Any

from .baidu_cloud import run_baidu_cloud_provider
from .importer import import_external_json
from .mock_provider import load_mock_ocr_result
from .models import CLOUD_PROVIDERS, OCR_PROVIDERS
from .normalizer import normalize_ocr_payload
from .paddleocr_local import run_paddleocr_local
from .paddleocr_vl_local import run_paddleocr_vl_local
from .report import write_handoff_summary, write_ocr_report
from .safety import safety_decision, scan_input_path, scan_payload_for_sensitive_data


def extract_ocr_evidence(
    input_path: Path,
    out_dir: Path,
    *,
    provider: str = "mock_ocr",
    allow_cloud_ocr: bool = False,
    no_cloud: bool = False,
    redact_before_cloud: bool = False,
    safety_evaluate: bool = False,
    model_dir: str | None = None,
    document_mode: str = "mixed",
    max_file_mb: int = 50,
    max_total_mb: int = 500,
) -> dict[str, Any]:
    if provider not in OCR_PROVIDERS:
        raise ValueError(f"unsupported OCR provider: {provider}")
    if not input_path.exists():
        raise FileNotFoundError(f"input not found: {input_path}")
    if provider in CLOUD_PROVIDERS and (no_cloud or not allow_cloud_ocr):
        raw = run_baidu_cloud_provider(provider, input_path, allow_cloud=False, input_findings=[], ocr_findings=[])
        safety = raw["safety_override"]
        ocr = normalize_ocr_payload(input_path, provider, "cloud", raw, safety)
        files = write_ocr_report(out_dir, ocr)
        write_handoff_summary(out_dir, ocr)
        return {"ocr": ocr, "files": files, "exit_code": 2}

    input_findings = scan_input_path(input_path)
    if provider == "mock_ocr":
        raw = load_mock_ocr_result(input_path)
        mode = "mock"
    elif provider == "external_json_import":
        raw = import_external_json(input_path)
        mode = "imported"
    elif provider == "paddleocr_local":
        raw = run_paddleocr_local(input_path)
        mode = "local"
    elif provider == "paddleocr_vl_local":
        raw = run_paddleocr_vl_local(input_path, model_dir=model_dir)
        mode = "local"
    else:
        raw = run_baidu_cloud_provider(
            provider,
            input_path,
            allow_cloud=allow_cloud_ocr,
            input_findings=input_findings,
            ocr_findings=[],
        )
        mode = "cloud"

    ocr_findings = scan_payload_for_sensitive_data(raw)
    if provider in CLOUD_PROVIDERS:
        raw = run_baidu_cloud_provider(
            provider,
            input_path,
            allow_cloud=allow_cloud_ocr,
            input_findings=input_findings,
            ocr_findings=ocr_findings,
        )
        safety = raw["safety_override"]
    else:
        safety = safety_decision(
            provider=provider,
            input_findings=input_findings,
            ocr_findings=ocr_findings,
            allow_cloud=False,
        )
    ocr = normalize_ocr_payload(input_path, provider, mode, raw, safety)
    ocr["document_mode"] = document_mode
    ocr["limits"] = {"max_file_mb": max_file_mb, "max_total_mb": max_total_mb}
    ocr["redact_before_cloud"] = bool(redact_before_cloud)
    files = write_ocr_report(out_dir, ocr)
    write_handoff_summary(out_dir, ocr)
    blocked = ocr["safety"]["shareability_decision"] == "blocked"
    return {"ocr": ocr, "files": files, "exit_code": 2 if blocked and provider in CLOUD_PROVIDERS else 0}
