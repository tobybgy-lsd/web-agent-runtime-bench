from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from .consistency import compare_ocr_dom, compare_ocr_vlm
from .extractor import extract_ocr_evidence
from .validation import validate_ocr_report


def handle_ocr_evidence(args: Namespace) -> int:
    command = args.ocr_command
    if command == "extract":
        result = extract_ocr_evidence(
            Path(args.input),
            Path(args.out),
            provider=args.provider,
            allow_cloud_ocr=bool(args.allow_cloud_ocr),
            no_cloud=bool(args.no_cloud),
            redact_before_cloud=bool(args.redact_before_cloud),
            safety_evaluate=bool(args.safety_evaluate),
            model_dir=args.model_dir,
            document_mode=args.document_mode,
            max_file_mb=args.max_file_mb,
            max_total_mb=args.max_total_mb,
        )
        ocr = result["ocr"]
        print("Agent Failure Doctor - OCR Evidence")
        print(f"Provider: {ocr.get('provider')}")
        print(f"Shareability: {ocr.get('safety', {}).get('shareability_decision')}")
        print(f"Cloud upload used: {ocr.get('safety', {}).get('cloud_upload_used')}")
        print(f"Output: {args.out}")
        return int(result["exit_code"])
    if command == "compare":
        report = compare_ocr_dom(Path(args.ocr), Path(args.dom), Path(args.out))
        print("Agent Failure Doctor - OCR DOM Consistency")
        print(f"Status: {report.get('status')}")
        print(f"Output: {args.out}")
        return 0
    if command == "compare-vlm":
        report = compare_ocr_vlm(Path(args.ocr), Path(args.vlm), Path(args.out))
        print("Agent Failure Doctor - OCR VLM Consistency")
        print(f"Status: {report.get('status')}")
        print(f"Output: {args.out}")
        return 0
    if command == "validate":
        report = validate_ocr_report(Path(args.input), Path(args.out))
        print("Agent Failure Doctor - OCR Evidence Validate")
        print(f"Status: {report.get('status')}")
        print(f"Output: {args.out}")
        return 0 if report.get("status") == "pass" else 1
    print(f"unsupported ocr-evidence command: {command}")
    return 2
