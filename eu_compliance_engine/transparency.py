from typing import Dict, Any

def inject_article_50_label(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Injects a standard metadata tag indicating AI-generated content into headers.
    This fulfills the machine-readability requirement of Article 50 of the EU AI Act.
    """
    if headers is None:
        headers = {}
    headers["x-ai-generated"] = "true"
    return headers
