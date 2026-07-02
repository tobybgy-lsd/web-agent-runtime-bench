import json
import re
import unittest
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "examples" / "realistic_playwright_traces"

FORBIDDEN_TRACE_FIELDS = (
    "storageStateExpected",
    "storageStateLoaded",
    "routeRegistered",
    "routeMatched",
    "harExpected",
    "harLoaded",
    "shadowHost",
    "elementExistsInShadowDom",
    "ordinaryLocatorFailed",
    "custom_observation",
)

SENSITIVE_PATTERNS = re.compile(
    r"password=|authorization:|bearer\s+|set-cookie|api_key|token=|secret",
    re.IGNORECASE,
)


class RealTraceFixtureIntegrityTests(unittest.TestCase):
    def test_realistic_trace_fixtures_exist_and_have_required_metadata(self):
        self.assertTrue(FIXTURE_ROOT.exists(), "examples/realistic_playwright_traces is required")
        cases = sorted(path for path in FIXTURE_ROOT.iterdir() if path.is_dir())
        self.assertGreaterEqual(len(cases), 30)
        for case_dir in cases:
            with self.subTest(case=case_dir.name):
                self.assertTrue((case_dir / "expected_diagnosis.json").exists())
                self.assertTrue((case_dir / "source.json").exists())
                source = json.loads((case_dir / "source.json").read_text(encoding="utf-8"))
                self.assertEqual(source.get("generated_by"), "tools/real_trace_generation/generate_real_trace_fixtures.py")
                self.assertFalse(source.get("contains_custom_observation_fields"))
                self.assertFalse(source.get("contains_credentials"))
                self.assertFalse(source.get("contains_real_third_party_data"))
                if (case_dir / "trace.zip").exists():
                    self._assert_trace_zip_is_clean(case_dir / "trace.zip", source)
                expected = json.loads((case_dir / "expected_diagnosis.json").read_text(encoding="utf-8"))
                if expected.get("failure_layer") == "anti_bot_risk":
                    self.assertTrue(expected.get("safe_next_action"))

    def _assert_trace_zip_is_clean(self, trace_zip: Path, source: dict):
        with ZipFile(trace_zip) as archive:
            names = archive.namelist()
            self.assertTrue(any(name.endswith("trace.trace") or name == "trace.trace" for name in names))
            text_parts = []
            for name in names:
                lower = name.lower()
                if lower.startswith("resources/src@"):
                    continue
                if lower.endswith((".trace", ".json", ".network", ".html")):
                    text_parts.append(archive.read(name).decode("utf-8", errors="ignore"))
        raw = "\n".join(text_parts)
        for forbidden in FORBIDDEN_TRACE_FIELDS:
            self.assertNotIn(forbidden, raw)
        if source.get("sanitized_dummy_cookie"):
            raw = raw.replace("Set-Cookie", "").replace("Cookie", "")
        self.assertIsNone(SENSITIVE_PATTERNS.search(raw))

