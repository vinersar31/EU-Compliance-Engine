import os
import json
from typing import Dict, Any, Optional
from google import genai

# Client initialization, defaults to None, populated on first use if not explicitly given
_client = None

def get_client(api_key: Optional[str] = None) -> genai.Client:
    global _client
    if _client is None:
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
             raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY environment variable.")
        _client = genai.Client(api_key=key)
    return _client

def evaluate_with_llm(solution_description: str, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
    """
    Evaluates a solution description using Gemini LLM to determine
    if it complies with the EU AI Act.
    """
    try:
        client = get_client()
        prompt = f"""
You are an expert on the EU AI Act (Regulation (EU) 2024/1689).
Analyze the following AI system solution description and provide an assessment of its compliance.
Respond in valid JSON format ONLY, with the following keys:
- "is_compliant" (boolean): True if it seems compliant, False if it seems prohibited or highly problematic without mitigation.
- "risk_level" (string): One of ["Minimal/No Risk", "Transparency Risk", "High Risk", "Unacceptable Risk (Prohibited)", "Systemic Risk GPAI", "Standard GPAI Risk"].
- "reasoning" (string): A short explanation of your assessment based on the EU AI Act.
- "suggested_categories" (list of strings): Any relevant categories (e.g. "social_scoring", "biometrics", "employment_hr").
- "suggested_features" (list of strings): Any relevant features (e.g. "profiling", "interaction_with_humans").

Solution Description:
{solution_description}
"""
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        # Attempt to parse the JSON response
        text = response.text.strip()
        # Handle cases where the model wraps the response in markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        return json.loads(text.strip())
    except Exception as e:
        return {
            "error": str(e),
            "is_compliant": False,
            "risk_level": "Unknown",
            "reasoning": f"Failed to evaluate with LLM: {str(e)}",
            "suggested_categories": [],
            "suggested_features": []
        }
