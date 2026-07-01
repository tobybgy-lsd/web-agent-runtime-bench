import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.failure_artifacts.bloom_deduper import BloomDedupeChecker, BloomFilter, optimal_bloom_params
from tools.failure_artifacts.classifier import classify_failure_artifact
from tools.failure_artifacts.data_quality_checker import (
    CheckpointManager,
    DataEngineeringPipeline,
    DeadLetterQueue,
    DedupeChecker,
    FieldQualityReporter,
    RetryPolicy,
    RunManifest,
    SchemaValidator,
    compare_source_hashes,
    compute_source_hash,
)
from tools.failure_artifacts.guardrails import forbidden_output_hits
from tools.failure_artifacts.resolution import generate_fix_plan
from tools.failure_artifacts.structured_logger import TraceContext, create_logger
from tools.failure_artifacts.visual_failure_doctor import diagnose_visual_failure
from tools.failure_artifacts.vlm_visual_analyzer import (
    analyze_png_basic,
    build_vlm_request,
    call_vlm_api,
    enhance_diagnosis_with_vlm,
)


def artifact(message: str, observations=None, status_code=403):
    return {
        "schema_version": "failure-artifact/v1",
        "run_id": "visual_data_public_pack",
        "tool": "playwright",
        "target_type": "sanitized_real_failure",
        "summary": "Public-safe diagnostic regression",
        "error": {"message": message, "stack": "", "status_code": status_code},
        "artifacts": {},
        "observations": observations or {},
        "expected": {},
        "actual": {},
        "labels": {"failure_type": "unknown", "confidence": 0.0},
        "safety": {
            "sanitized": True,
            "contains_credentials": False,
            "external_network_required": False,
            "user_authorized_or_synthetic": True,
        },
    }


def assert_no_mojibake(testcase: unittest.TestCase, value):
    text = json.dumps(value, ensure_ascii=False)
    for marker in ("鈿", "馃", "涓", "鏁", "瑙", "鎴", "锛", "熵"):
        testcase.assertNotIn(marker, text)


class DataQualityPublicPackTests(unittest.TestCase):
    def test_schema_dedupe_checkpoint_retry_dlq_manifest_and_quality_are_reusable(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)

            validator = SchemaValidator({"title": str, "price": float, "url": str})
            invalid = validator.validate({"title": "A", "price": "9.9"})
            self.assertFalse(invalid["ok"])
            self.assertTrue(any("MISSING field: 'url'" in item for item in invalid["errors"]))
            self.assertTrue(any("TYPE_MISMATCH field: 'price'" in item for item in invalid["errors"]))

            deduper = DedupeChecker(["url"])
            self.assertFalse(deduper.is_duplicate({"url": "https://example.test/a"}))
            self.assertTrue(deduper.is_duplicate({"url": "https://example.test/a"}))
            self.assertEqual(deduper.report()["duplicates_found"], 1)

            checkpoint = CheckpointManager(out / "checkpoint.json")
            checkpoint.mark_page_done(7)
            checkpoint.set("cursor", "next-7")
            reloaded = CheckpointManager(out / "checkpoint.json")
            self.assertTrue(reloaded.is_page_done(7))
            self.assertEqual(reloaded.get("cursor"), "next-7")

            retry = RetryPolicy(max_retries=2, base_delay=0.01, max_delay=0.05)
            self.assertTrue(retry.can_retry())
            self.assertLessEqual(retry.next_delay(), 0.06)
            self.assertTrue(retry.can_retry())
            retry.next_delay()
            self.assertFalse(retry.can_retry())

            dlq = DeadLetterQueue(out / "dead_letter_queue.json")
            dlq.push("https://example.test/b", "schema_error", {"id": 1})
            self.assertEqual(dlq.flush(), 1)
            self.assertEqual(len(json.loads((out / "dead_letter_queue.json").read_text(encoding="utf-8"))), 1)

            manifest = RunManifest(out / "run_manifest.json")
            manifest.update(records_total=2, records_valid=1)
            manifest.finish("success")
            self.assertEqual(json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))["status"], "success")

            reporter = FieldQualityReporter(["title", "price"])
            reporter.ingest({"title": "A", "price": 1.0}, {"title": str, "price": float})
            reporter.ingest({"title": "", "price": "bad"}, {"title": str, "price": float})
            report = reporter.report()
            self.assertEqual(report["total_records"], 2)
            self.assertEqual(report["fields"]["price"]["type_errors"], 1)
            assert_no_mojibake(self, report)

    def test_pipeline_and_source_hash_produce_stable_public_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = DataEngineeringPipeline(
                schema={"title": str, "price": float, "url": str},
                dedupe_keys=["url"],
                output_dir=tmp,
            )
            ok = pipeline.process_record({"title": "A", "price": 1.0, "url": "u1"})
            duplicate = pipeline.process_record({"title": "A", "price": 1.0, "url": "u1"})
            bad = pipeline.process_record({"title": "B", "price": "bad", "url": "u2"})

            self.assertEqual(ok["status"], "ok")
            self.assertEqual(duplicate["status"], "duplicate")
            self.assertEqual(bad["status"], "schema_error")

            report_path = pipeline.save_final_report()
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["deduplication"]["duplicates_found"], 1)
            assert_no_mojibake(self, report)

            old_hash = compute_source_hash("<html>old</html>")
            new_hash = compute_source_hash("<html>new</html>")
            change = compare_source_hashes(new_hash, old_hash)
            self.assertTrue(change["source_changed"])
            self.assertIn("changed", change["alert"].lower())
            assert_no_mojibake(self, change)

    def test_bloom_deduper_has_bounded_stats_and_stub_is_explicit(self):
        bit_count, hash_count = optimal_bloom_params(1000, 0.01)
        self.assertGreater(bit_count, 0)
        self.assertGreaterEqual(hash_count, 1)

        bloom = BloomFilter(capacity=100, false_positive_rate=0.01)
        self.assertFalse(bloom.is_probably_duplicate("url-1"))
        self.assertTrue(bloom.is_probably_duplicate("url-1"))
        self.assertLessEqual(bloom.stats()["estimated_fpr"], 1.0)

        checker = BloomDedupeChecker(["url"], capacity=100, fpr=0.01)
        self.assertFalse(checker.is_duplicate({"url": "https://example.test/1"}))
        self.assertTrue(checker.is_duplicate({"url": "https://example.test/1"}))
        report = checker.report()
        self.assertEqual(report["duplicates_found"], 1)
        self.assertIn("bloom_stats", report)

    def test_structured_logger_writes_jsonl_trace_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = create_logger(tmp, run_id="run_public", also_print=False)
            try:
                ctx = TraceContext(run_id="run_public").with_page(2, "https://example.test/page/2")
                record_ctx = ctx.with_record(3, "https://example.test/item/3")
                logger.log_page(ctx, page_num=2, count=10, elapsed_ms=123.4)
                logger.log_record(record_ctx, {"id": "item-3", "title": "Example"}, "ok", [])
                logger.log_field_quality(ctx, {"total_records": 10, "fields": {"title": {"quality": "good"}}})
                summary = logger.summary()
            finally:
                logger.close()

            log_path = Path(tmp) / "structured_run.jsonl"
            rows = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["run_id"], "run_public")
            self.assertEqual(rows[0]["page_num"], 2)
            self.assertEqual(rows[1]["record_idx"], 3)
            self.assertEqual(summary["records_logged"], 1)
            assert_no_mojibake(self, rows)


class VisualPublicPackTests(unittest.TestCase):
    def test_visual_diagnosis_detects_overlay_coordinate_drift_loading_ocr_and_dom_inconsistency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\nstub")
            (root / "dom_snapshot.html").write_text(
                "<div class='modal overlay' role='dialog' aria-modal='true'></div>"
                "<div class='skeleton' aria-busy='true'></div>"
                "<button style='display:none'>Buy</button>",
                encoding="utf-8",
            )
            (root / "click_coordinates.json").write_text(
                json.dumps(
                    {
                        "device_scale_factor": 2.0,
                        "click_x": 10,
                        "click_y": 10,
                        "target_bounding_box": {"x": 100, "y": 100, "width": 20, "height": 20},
                    }
                ),
                encoding="utf-8",
            )
            (root / "ocr_excerpt.txt").write_text("Total: ??", encoding="utf-8")

            result = diagnose_visual_failure(root)

            self.assertEqual(result["diagnosis_type"], "visual_failure")
            self.assertEqual(result["primary_failure_type"], "overlay_blocked")
            self.assertIn("viewport_scale_drift", result["all_failure_types"])
            self.assertIn("coordinate_drift", result["all_failure_types"])
            self.assertIn("screenshot_not_loaded", result["all_failure_types"])
            self.assertIn("ocr_mismatch", result["all_failure_types"])
            self.assertIn("screenshot_dom_inconsistency", result["all_failure_types"])
            self.assertGreaterEqual(result["confidence"], 0.9)
            assert_no_mojibake(self, result)
            combined = json.dumps(result, ensure_ascii=False).lower()
            self.assertFalse(forbidden_output_hits(combined))

    def test_visual_diagnose_cli_writes_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "run"
            out = Path(tmp) / "report"
            root.mkdir()
            (root / "dom_snapshot.html").write_text("<div class='modal' role='dialog'></div>", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, "-m", "failure_doctor", "visual-diagnose", str(root), "--out", str(out)],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("Visual Diagnosis", completed.stdout)
            report = json.loads((out / "visual_diagnosis.json").read_text(encoding="utf-8"))
            self.assertEqual(report["primary_failure_type"], "overlay_blocked")
            assert_no_mojibake(self, report)

    def test_vlm_mock_enhancement_is_local_and_does_not_require_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            screenshot = root / "screenshot.png"
            screenshot.write_bytes(b"\x89PNG\r\n\x1a\nstub")

            basic = analyze_png_basic(screenshot)
            self.assertEqual(basic["error"], "could not parse IHDR")

            pack = build_vlm_request(screenshot, prompt_key="general_failure")
            response = call_vlm_api(pack, provider="mock")
            self.assertEqual(response["provider"], "mock")
            self.assertIn("parsed", response)

            diagnosis = {
                "primary_failure_type": "unknown_visual",
                "confidence": 0.3,
                "confidence_label": "30%",
                "findings": [],
            }
            enhanced = enhance_diagnosis_with_vlm(diagnosis, root, provider="mock")
            self.assertIn("vlm_analysis", enhanced)
            self.assertFalse(enhanced["vlm_upgraded_diagnosis"])
            assert_no_mojibake(self, enhanced)


class PublicSafeRuntimeSubtypeTests(unittest.TestCase):
    def test_audio_tcp_and_ast_signals_have_precise_safe_subtypes(self):
        samples = {
            "audio_fingerprint_risk": artifact(
                "Audio fingerprint risk: virtualized audio device detected in sanitized runtime report",
                {"log_excerpt": "audio hardware detected as virtualized audio in authorized test telemetry"},
            ),
            "tcp_ip_os_fingerprint_mismatch": artifact(
                "TCP/IP OS fingerprint mismatch: p0f reports Linux while browser metadata claims Windows",
                {"log_excerpt": "tcp/ip os mismatch evidence collected from sanitized transport summary"},
            ),
            "ast_dynamic_token_required": artifact(
                "AST dynamic token required: rotated string array and dynamic token missing after bundle update",
                {"log_excerpt": "sanitized AST rotation evidence indicates client-generated request integrity token"},
            ),
        }

        for expected_subtype, sample in samples.items():
            with self.subTest(expected_subtype=expected_subtype):
                diagnosis = classify_failure_artifact(sample)
                combined = json.dumps(diagnosis, ensure_ascii=False).lower()

                self.assertEqual(diagnosis["failure_type"], "anti_bot_risk")
                self.assertEqual(diagnosis["subtype"], expected_subtype)
                self.assertIn("authorization", combined)
                self.assertFalse(forbidden_output_hits(combined))


class DataEngineeringClosedLoopTriageTests(unittest.TestCase):
    def test_data_engineering_failures_have_precise_subtypes_and_safe_fix_plans(self):
        samples = {
            "schema_validation_failure": (
                artifact(
                    "Schema validation failed: missing required field price; expected float got str",
                    {"log_excerpt": "field validation failed before persistence"},
                    status_code=0,
                ),
                "SchemaValidator",
            ),
            "duplicate_submission": (
                artifact(
                    "Retry caused duplicate submission: duplicate key already exists for url",
                    {"log_excerpt": "idempotency key missing, submitted twice"},
                    status_code=409,
                ),
                "BloomDedupeChecker",
            ),
            "checkpoint_missing": (
                artifact(
                    "Cannot resume: checkpoint file checkpoint.json not found after restart from page 42",
                    {"log_excerpt": "state not saved before process restart"},
                    status_code=0,
                ),
                "CheckpointManager",
            ),
            "dead_letter_overflow": (
                artifact(
                    "Dead letter queue overflow: exceeded max retries for many failed records",
                    {"log_excerpt": "DLQ contains permanently failed records"},
                    status_code=0,
                ),
                "DeadLetterQueue",
            ),
            "pagination_data_loss": (
                artifact(
                    "Pagination data loss: duplicate records on pages 4-5 and expected records count mismatch",
                    {"log_excerpt": "page overlap with missing records at page boundary"},
                    status_code=0,
                ),
                "FieldQualityReporter",
            ),
        }

        for expected_subtype, (sample, expected_tool) in samples.items():
            with self.subTest(expected_subtype=expected_subtype):
                diagnosis = classify_failure_artifact(sample)
                self.assertEqual(diagnosis["failure_type"], "data_engineering")
                self.assertEqual(diagnosis["subtype"], expected_subtype)

                plan = generate_fix_plan(diagnosis)
                combined = json.dumps(plan, ensure_ascii=False)
                self.assertEqual(plan["failure_type"], "data_engineering")
                self.assertIn(expected_tool, combined)
                advisory_plan = dict(plan)
                advisory_plan.pop("forbidden_actions", None)
                self.assertFalse(forbidden_output_hits(json.dumps(advisory_plan, ensure_ascii=False).lower()))
                assert_no_mojibake(self, diagnosis)
                assert_no_mojibake(self, plan)

    def test_pagination_overlap_wins_over_duplicate_submission(self):
        diagnosis = classify_failure_artifact(
            artifact(
                "duplicate records on pages 4-5; pagination boundary drift caused expected records mismatch",
                {"log_excerpt": "duplicate records were observed across adjacent pages, not duplicate submission"},
                status_code=0,
            )
        )

        self.assertEqual(diagnosis["failure_type"], "data_engineering")
        self.assertEqual(diagnosis["subtype"], "pagination_data_loss")


if __name__ == "__main__":
    unittest.main()
