import unittest
from eu_compliance_engine.agent_tool import AISystemDefinition, GPAIInfo, generate_compliance_report

class TestAgentTool(unittest.TestCase):

    def test_generate_compliance_report_as_tool(self):
        # Create a pydantic model instance
        system_def = AISystemDefinition(
            name="Test AI System",
            description="A test system for the agent tool.",
            categories=["employment_hr"],
            features=["profiling"],
            exceptions=["improves_human_activity"],
            gpai=GPAIInfo(is_gpai=False)
        )

        # Call the tool function
        report = generate_compliance_report(system_def)

        # Verify it generates a report correctly
        self.assertIn("Test AI System", report)
        self.assertIn("A test system for the agent tool.", report)
        self.assertIn("High Risk", report)

if __name__ == '__main__':
    unittest.main()
