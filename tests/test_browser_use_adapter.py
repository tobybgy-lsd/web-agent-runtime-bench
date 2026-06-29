import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.cli import build_artifact, collect_inputs
from integrations.browser_use.adapter import convert_browser_use_run
from tools.failure_artifacts.diagnose import diagnose_artifact


class BrowserUseAdapterTests(unittest.TestCase):
    def test_converts_agent_history_to_diagnosable_failure_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "agent_history.json"
            source.write_text(
                json.dumps(
                    {
                        "task": "download local mock export",
                        "steps": [
                            {"action": "click", "target": "Export"},
                            {"action": "download", "error": "Download event fired but file was not saved"},
                        ],
                        "final_error": "Download event fired but file was not saved; acceptDownloads is false",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            out = tmp_path / "failure_pack"

            pack = convert_browser_use_run(source, out)

            self.assertTrue((out / "error.log").exists())
            self.assertTrue((out / "agent_steps.json").exists())
            self.assertTrue((out / "user_description.txt").exists())
            self.assertEqual(pack["adapter"], "browser_use")
            artifact = build_artifact(collect_inputs(out))
            diagnosis = diagnose_artifact(artifact)
            self.assertEqual(diagnosis["failure_type"], "playwright_download")

    def test_converts_repeated_action_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "browser-use.log"
            source.write_text(
                "Agent repeatedly executed the same action; extract_content action repeated and unknown led to infinite loop",
                encoding="utf-8",
            )
            out = tmp_path / "failure_pack"

            convert_browser_use_run(source, out)
            artifact = build_artifact(collect_inputs(out))
            diagnosis = diagnose_artifact(artifact)
            self.assertEqual(diagnosis["failure_type"], "agent_repetition_loop")


if __name__ == "__main__":
    unittest.main()
