import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "public_failure_corpus"
REQUIRED_FIELDS = {
    "case_id",
    "source_url",
    "source_type",
    "symptom",
    "raw_error_excerpt",
    "input_available",
    "likely_user_facing_category",
    "likely_technical_category",
    "evidence",
    "reported_fix",
    "next_action_expected",
    "can_convert_to_template",
}


class PublicFailureCorpusTests(unittest.TestCase):
    def test_public_failure_corpus_has_at_least_150_complete_cases(self):
        case_files = sorted((CORPUS / "cases").glob("*.yaml"))
        records = []
        for case_file in case_files:
            for chunk in case_file.read_text(encoding="utf-8").split("\n---\n"):
                if "case_id:" in chunk:
                    records.append((case_file, chunk))
        self.assertGreaterEqual(len(records), 150)

        convertible = 0
        source_groups = set()
        for case_file, text in records:
            fields = {line.split(":", 1)[0] for line in text.splitlines() if line and not line.startswith(" ")}
            self.assertTrue(REQUIRED_FIELDS.issubset(fields), case_file.name)
            self.assertNotIn("cookie:", text.lower(), case_file.name)
            self.assertNotIn("authorization:", text.lower(), case_file.name)
            if "can_convert_to_template: yes" in text:
                convertible += 1
            for line in text.splitlines():
                if line.startswith("source_type:"):
                    source_groups.add(line.split(":", 1)[1].strip())

        self.assertGreaterEqual(convertible, 10)
        self.assertGreaterEqual(len(source_groups), 4)

    def test_public_failure_corpus_has_summary_files(self):
        for name in ("README.md", "schema.json", "sources.md", "findings.md"):
            self.assertTrue((CORPUS / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
