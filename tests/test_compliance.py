import unittest
from eu_compliance_engine.compliance_engine import ComplianceEngine

class TestComplianceEngine(unittest.TestCase):

    def test_prohibited_system(self):
        system = {
            "name": "Social Credit System",
            "categories": ["social_scoring"]
        }
        engine = ComplianceEngine(system)
        result = engine.evaluate()
        self.assertTrue(result["is_prohibited"])
        self.assertEqual(result["risk_level"], "Unacceptable Risk (Prohibited)")

    def test_high_risk_system(self):
        system = {
            "name": "HR Recruitment Tool",
            "categories": ["employment_hr"]
        }
        engine = ComplianceEngine(system)
        result = engine.evaluate()
        self.assertFalse(result["is_prohibited"])
        self.assertTrue(result["is_high_risk"])
        self.assertTrue(result["requires_conformity_assessment"])
        self.assertEqual(result["risk_level"], "High Risk")

    def test_high_risk_exception(self):
        system = {
            "name": "Grammar Checker",
            "categories": ["education"],
            "exceptions": ["improves_human_activity"]
        }
        engine = ComplianceEngine(system)
        result = engine.evaluate()
        self.assertFalse(result["is_high_risk"])
        self.assertFalse(result["requires_conformity_assessment"])
        self.assertEqual(result["risk_level"], "Minimal/No Risk (Exception Applied)")

    def test_high_risk_exception_override_by_profiling(self):
        system = {
            "name": "Resume Profiler",
            "categories": ["employment_hr"],
            "features": ["profiling"],
            "exceptions": ["improves_human_activity"]
        }
        engine = ComplianceEngine(system)
        result = engine.evaluate()
        self.assertTrue(result["is_high_risk"])
        self.assertTrue(result["requires_conformity_assessment"])
        self.assertEqual(result["risk_level"], "High Risk")

    def test_transparency_obligations(self):
        system = {
            "name": "Customer Support Chatbot",
            "features": ["interaction_with_humans", "generates_content"]
        }
        engine = ComplianceEngine(system)
        result = engine.evaluate()
        self.assertEqual(len(result["transparency_obligations"]), 2)
        self.assertTrue(any("Interaction Disclosure" in obs for obs in result["transparency_obligations"]))
        self.assertTrue(any("Content Marking" in obs for obs in result["transparency_obligations"]))

    def test_systemic_risk_gpai(self):
        system = {
            "name": "Massive Language Model",
            "gpai": {
                "is_gpai": True,
                "flops": 2e25
            }
        }
        engine = ComplianceEngine(system)
        result = engine.evaluate()
        self.assertEqual(len(result["gpai_obligations"]), 1)
        self.assertTrue(any("Systemic Risk GPAI" in obs for obs in result["gpai_obligations"]))
        self.assertEqual(result["risk_level"], "Systemic Risk GPAI")

    def test_standard_gpai(self):
        system = {
            "name": "Smaller Language Model",
            "gpai": {
                "is_gpai": True,
                "flops": 5e24
            }
        }
        engine = ComplianceEngine(system)
        result = engine.evaluate()
        self.assertEqual(len(result["gpai_obligations"]), 1)
        self.assertTrue(any("Standard GPAI" in obs for obs in result["gpai_obligations"]))
        self.assertEqual(result["risk_level"], "Standard GPAI Risk")

if __name__ == '__main__':
    unittest.main()
