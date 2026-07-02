import json
import tempfile
import unittest
from pathlib import Path

from failure_doctor.auto_collect import watch_project_once


class AutoCollectorWatchTests(unittest.TestCase):
    def test_watch_once_writes_event_and_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "error.log").write_text("Timeout waiting for selector .submit\n", encoding="utf-8")
            out = Path(tmp) / "watch"

            summary = watch_project_once(root, out, preset="auto", auto_diagnose=True)

            self.assertGreaterEqual(summary["events_seen"], 1)
            self.assertTrue((out / "watch_events.jsonl").exists())
            self.assertTrue((out / "watch_summary.md").exists())
            runs = list((out / "runs").iterdir())
            self.assertEqual(len(runs), 1)
            event = json.loads((out / "watch_events.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("relative_path", event)


