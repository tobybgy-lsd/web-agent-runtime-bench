import tempfile
import unittest
from pathlib import Path

from failure_doctor.agent_invocation import bootstrap_agent_frontend


class AgentBootstrapEnterpriseGovernanceTests(unittest.TestCase):
    def test_bootstrap_writes_enterprise_governance_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = bootstrap_agent_frontend(Path(tmp), target="generic_agent")
            workflow = Path(result["agents_root"]) / result["targets"][0] / "enterprise_governance_workflow.md"
            text = workflow.read_text(encoding="utf-8")
            self.assertIn("Check role and policy before acting", text)
            self.assertIn("Never bypass approval", text)
            self.assertIn("All actions must be audit logged", text)


if __name__ == "__main__":
    unittest.main()
