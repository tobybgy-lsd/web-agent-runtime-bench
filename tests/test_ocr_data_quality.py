from __future__ import annotations

from unittest import TestCase

from failure_doctor.ocr_evidence.quality import build_ocr_data_quality_report


class OcrDataQualityTests(TestCase):
    def test_detects_table_column_shift_and_form_type_issues(self) -> None:
        report = build_ocr_data_quality_report(
            {
                "tables": [{"id": "t1", "columns": 1, "cells": [["Name"], ["A"]], "warnings": ["possible_column_shift"]}],
                "forms": [{"id": "f1", "fields": [{"label": "Price", "value": "nineteen"}]}],
            }
        )
        types = {finding["type"] for finding in report["findings"]}
        self.assertIn("ocr_table_column_shift", types)
        self.assertIn("price_field_not_numeric", types)
