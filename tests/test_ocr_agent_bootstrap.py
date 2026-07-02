from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase

from failure_doctor.agent_invocation import bootstrap_agent_frontend


class OcrAgentBootstrapTests(TestCase):
    def test_agent_bootstrap_includes_ocr_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            bootstrap_agent_frontend(project, target="codex")
            workflow = project / ".failure-doctor" / "agents" / "codex" / "ocr_evidence_workflow.md"
            text = workflow.read_text(encoding="utf-8")
            self.assertIn("ocr-evidence extract", text)
            self.assertIn("Do not upload screenshots or PDFs", text)

