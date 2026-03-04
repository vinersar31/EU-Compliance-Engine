import unittest
from unittest.mock import patch, MagicMock
from eu_compliance_engine.llm_evaluator import evaluate_with_llm

class TestLLMEvaluator(unittest.TestCase):

    @patch('eu_compliance_engine.llm_evaluator.get_client')
    def test_evaluate_with_llm_success(self, MockGetClient):
        # Mocking the Gemini response
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "is_compliant": false,
            "risk_level": "Unacceptable Risk (Prohibited)",
            "reasoning": "This is a social scoring system.",
            "suggested_categories": ["social_scoring"],
            "suggested_features": ["profiling"]
        }
        '''
        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.return_value = mock_response
        MockGetClient.return_value = mock_client_instance

        result = evaluate_with_llm("An AI system that scores citizens based on behavior.")

        self.assertFalse(result["is_compliant"])
        self.assertEqual(result["risk_level"], "Unacceptable Risk (Prohibited)")
        self.assertIn("social_scoring", result["suggested_categories"])

    @patch('eu_compliance_engine.llm_evaluator.get_client')
    def test_evaluate_with_llm_failure(self, MockGetClient):
        # Mock an error during generation
        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.side_effect = Exception("API Error")
        MockGetClient.return_value = mock_client_instance

        result = evaluate_with_llm("A simple grammar checker.")

        self.assertIn("error", result)
        self.assertIn("API Error", result["error"])

if __name__ == '__main__':
    unittest.main()
