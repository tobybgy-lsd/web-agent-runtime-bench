import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PositioningRoadmapTests(unittest.TestCase):
    def test_roadmap_names_current_engine_limits_and_next_packs(self):
        roadmap = (ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")

        self.assertIn("deterministic evidence-based diagnostic engine", roadmap)
        self.assertIn("does not claim to solve arbitrary failures", roadmap)
        self.assertIn("Composite Diagnosis Pack", roadmap)
        self.assertIn("Cross-Framework Adapter Pack", roadmap)
        self.assertIn("HTML Report Viewer", roadmap)
        self.assertIn("Reasoning Assist Layer", roadmap)
        self.assertIn("community-submitted failure cases", roadmap)

    def test_architecture_describes_agent_failure_doctor_not_only_old_benchmark(self):
        architecture = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")

        self.assertIn("Agent Failure Doctor", architecture)
        self.assertIn("trace/log/network/description/screenshot metadata", architecture)
        self.assertIn("diagnose -> plan -> verify", architecture)
        self.assertIn("rule engine", architecture)
        self.assertIn("optional reasoning assist", architecture)

    def test_readme_uses_professional_engine_positioning(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        normalized_readme = " ".join(readme.split())

        self.assertIn("deterministic evidence-based diagnostic engine", normalized_readme)
        self.assertIn("explainable classification", normalized_readme)
        self.assertIn("known automation failure patterns", normalized_readme)


if __name__ == "__main__":
    unittest.main()

