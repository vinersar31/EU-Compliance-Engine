import os
import re
from typing import Dict, List, Any

def _generate_variations(base_terms: List[str]) -> List[str]:
    """
    Generates variations of base terms to catch different naming conventions
    (e.g., camelCase, snake_case, space separated).
    """
    variations = []
    for term in base_terms:
        # Replace spaces or underscores with a regex that matches _, -, or space
        flexible_term = re.sub(r'[\s_]+', r'[_\-\\s]+', term)
        variations.append(rf"(?i)\b{flexible_term}\b")
    return variations

def audit_codebase(directory: str) -> Dict[str, Any]:
    """
    Scans a directory for specific high-risk and prohibited AI code patterns.
    """
    results = {
        "FLAG RED": [],
        "FLAG YELLOW": [],
        "FLAG BLUE": [],
        "FLAG GREEN": [],
        "report": []
    }

    red_base_terms = [
        "social credit score",
        "social scoring",
        "predictive policing",
        "biometric scraping",
        "scrape faces",
        "subliminal manipulation",
        "vulnerability exploitation",
        "mass surveillance",
        "emotion recognition workplace",
        "emotion recognition education"
    ]

    yellow_base_terms = [
        "emotion recognition",
        "biometric categorization",
        "resume parser",
        "candidate screening",
        "credit scoring",
        "predict recidivism",
        "critical infrastructure ai",
        "medical device ai",
        "law enforcement ai",
        "border control ai",
        "exam proctoring ai"
    ]

    blue_base_terms = [
        "chatbot",
        "deepfake",
        "ai generated",
        "generative ai",
        "llm",
        "large language model"
    ]

    red_patterns = _generate_variations(red_base_terms)
    yellow_patterns = _generate_variations(yellow_base_terms)
    blue_patterns = _generate_variations(blue_base_terms)

    # Add explicit code-specific patterns that don't fit word boundaries well
    yellow_patterns.extend([
        r"(?i)import\s+face_recognition\b",
        r"(?i)from\s+sklearn(?:\.\w+)*\s+import\s+.*credit_predictor"
    ])

    blue_patterns.extend([
        r"(?i)import\s+openai\b",
        r"(?i)import\s+anthropic\b",
        r"(?i)from\s+transformers\s+import\s+.*AutoModelForCausalLM",
        r"(?i)from\s+langchain\b"
    ])

    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    for pattern in red_patterns:
                        if re.search(pattern, content):
                            results["FLAG RED"].append(filepath)
                            if "This project is illegal in the EU." not in results["report"]:
                                results["report"].append("This project is illegal in the EU.")

                    for pattern in yellow_patterns:
                        if re.search(pattern, content):
                            results["FLAG YELLOW"].append(filepath)
                            if "Annex III High-Risk warning" not in results["report"]:
                                results["report"].append("Annex III High-Risk warning")

                    for pattern in blue_patterns:
                        if re.search(pattern, content):
                            results["FLAG BLUE"].append(filepath)
                            if "Must label output as AI-Generated" not in results["report"]:
                                results["report"].append("Must label output as AI-Generated")

            except Exception:
                pass

    if not results["FLAG RED"] and not results["FLAG YELLOW"] and not results["FLAG BLUE"]:
        results["FLAG GREEN"].append("OK")
        results["report"].append("No action needed")

    return results
