import os
import re
from typing import Dict, List, Any

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

    red_patterns = [
        r"social_credit_score",
        r"biometric_scraping"
    ]

    yellow_patterns = [
        r"import face_recognition",
        r"from sklearn import credit_predictor"
    ]

    blue_patterns = [
        r"chatbot",
        r"deepfake",
        r"ai_generated"
    ]

    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    for pattern in red_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            results["FLAG RED"].append(filepath)
                            if "This project is illegal in the EU." not in results["report"]:
                                results["report"].append("This project is illegal in the EU.")

                    for pattern in yellow_patterns:
                        if re.search(pattern, content):
                            results["FLAG YELLOW"].append(filepath)
                            if "Annex III High-Risk warning" not in results["report"]:
                                results["report"].append("Annex III High-Risk warning")

                    for pattern in blue_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            results["FLAG BLUE"].append(filepath)
                            if "Must label output as AI-Generated" not in results["report"]:
                                results["report"].append("Must label output as AI-Generated")

            except Exception:
                pass

    if not results["FLAG RED"] and not results["FLAG YELLOW"] and not results["FLAG BLUE"]:
        results["FLAG GREEN"].append("OK")
        results["report"].append("No action needed")

    return results
