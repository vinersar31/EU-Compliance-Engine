import unittest
from eu_compliance_engine.compliance_engine import ComplianceEngine

class TestIntegration(unittest.TestCase):
    def test_full_compliance_report_generation(self):
        # A full system definition that exercises multiple parts of the engine
        sample_system = {
            "name": "HR Resume Screening Assistant",
            "description": "An AI system that evaluates candidate resumes for job matching and ranks them.",
            "categories": ["employment_hr"],
            "features": ["profiling", "interaction_with_humans"],
            "exceptions": ["improves_human_activity"],
            "gpai": {
                "is_gpai": True,
                "flops": 5e24
            }
        }

        engine = ComplianceEngine(sample_system)

        # Call evaluate to generate the raw result to check first
        result = engine.evaluate()

        self.assertFalse(result["is_prohibited"])
        self.assertTrue(result["is_high_risk"])
        self.assertTrue(result["requires_conformity_assessment"])
        self.assertEqual(result["risk_level"], "High Risk")
        self.assertTrue(any("Standard GPAI" in obs for obs in result["gpai_obligations"]))
        self.assertTrue(any("Interaction Disclosure" in obs for obs in result["transparency_obligations"]))

        # Now call generate_report and verify the markdown output
        report = engine.generate_report()

        # Basic checks on the markdown content based on the actual output structure
        self.assertIn("# EU AI Act Conformity Assessment Report", report)
        self.assertIn("**System Name:** HR Resume Screening Assistant", report)
        self.assertIn("**Risk Level Classification:** High Risk", report)
        self.assertIn("## 1. Prohibited AI Practices (Article 5)", report)
        self.assertIn("✅ No prohibited practices detected.", report)
        self.assertIn("## 2. High-Risk AI Systems (Article 6 & Annex III)", report)
        self.assertIn("The system falls under the following High-Risk categories:", report)
        self.assertIn("- employment_hr", report)
        self.assertIn("**Conformity Assessment Required:** YES", report)
        self.assertIn("## 3. Transparency Obligations (Article 50)", report)
        self.assertIn("Interaction Disclosure", report)
        self.assertIn("## 4. General Purpose AI (GPAI) Models (Article 51-55)", report)
        self.assertIn("Standard GPAI:", report)

if __name__ == '__main__':
    unittest.main()
