import json
from typing import Dict, List, Any

class ComplianceEngine:
    """
    Evaluates an AI system against the EU AI Act (2026 standards) and generates a Conformity Assessment Report.
    """

    # Categories defined in the EU AI Act
    PROHIBITED_CATEGORIES = [
        "subliminal_techniques",
        "vulnerability_exploitation",
        "social_scoring",
        "predictive_policing",
        "biometric_scraping"
    ]

    HIGH_RISK_CATEGORIES = [
        "biometrics",
        "critical_infrastructure",
        "education",
        "employment_hr",
        "essential_services",
        "law_enforcement",
        "migration_border_control"
    ]

    def __init__(self, system_definition: Dict[str, Any]):
        """
        Initialize the compliance engine with a system definition.

        Expected keys in system_definition:
        - name: str
        - description: str
        - categories: List[str] (list of categories the system falls into)
        - features: List[str] (e.g., 'profiling', 'interaction_with_humans', 'generates_content', 'deepfakes')
        - exceptions: List[str] (e.g., 'narrow_procedural_task', 'improves_human_activity', 'detects_patterns')
        - gpai: Dict[str, Any] (e.g., {"is_gpai": True, "flops": 1e26})
        """
        self.system = system_definition
        self.name = self.system.get("name", "Unknown System")
        self.description = self.system.get("description", "No description provided.")
        self.categories = self.system.get("categories", [])
        self.features = self.system.get("features", [])
        self.exceptions = self.system.get("exceptions", [])
        self.gpai = self.system.get("gpai", {})

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluates the system and returns a compliance status dictionary.
        """
        result = {
            "is_prohibited": False,
            "prohibited_reasons": [],
            "is_high_risk": False,
            "high_risk_categories": [],
            "high_risk_exceptions_applied": [],
            "requires_conformity_assessment": False,
            "requires_ce_marking": False,
            "transparency_obligations": [],
            "gpai_obligations": [],
            "risk_level": "Minimal/No Risk"
        }

        # 1. Check Prohibited Practices
        for cat in self.categories + self.features:
            if cat in self.PROHIBITED_CATEGORIES:
                result["is_prohibited"] = True
                result["prohibited_reasons"].append(cat)

        if result["is_prohibited"]:
            result["risk_level"] = "Unacceptable Risk (Prohibited)"
            return result

        # 2. Check High-Risk Systems
        high_risk_cats = [cat for cat in self.categories if cat in self.HIGH_RISK_CATEGORIES]

        if high_risk_cats:
            result["high_risk_categories"] = high_risk_cats
            result["is_high_risk"] = True

            # 3. Check High-Risk Exceptions
            is_profiling = "profiling" in self.features
            if not is_profiling and self.exceptions:
                result["high_risk_exceptions_applied"] = self.exceptions
                result["is_high_risk"] = False
                result["risk_level"] = "Minimal/No Risk (Exception Applied)"
            else:
                result["requires_conformity_assessment"] = True
                result["requires_ce_marking"] = True
                result["risk_level"] = "High Risk"
                if is_profiling and self.exceptions:
                    result["high_risk_exceptions_applied"] = ["Exceptions ignored because system performs profiling"]

        # 4. Transparency Obligations
        if "interaction_with_humans" in self.features:
            result["transparency_obligations"].append("Interaction Disclosure: Users must be informed they are interacting with an AI.")
        if "generates_content" in self.features:
            result["transparency_obligations"].append("Content Marking: AI-generated text/images must be marked in a machine-readable format.")
        if "deepfakes" in self.features:
            result["transparency_obligations"].append("Deepfakes: Must be clearly labeled as manipulated content.")

        # 5. GPAI Obligations
        if self.gpai.get("is_gpai"):
            flops = self.gpai.get("flops", 0)
            if flops > 1e25:
                result["gpai_obligations"].append("Systemic Risk GPAI: Requires adversarial testing and systemic risk mitigation.")
                if result["risk_level"] == "Minimal/No Risk":
                    result["risk_level"] = "Systemic Risk GPAI"
            else:
                result["gpai_obligations"].append("Standard GPAI: Must provide technical documentation and instructions for use.")
                if result["risk_level"] == "Minimal/No Risk":
                    result["risk_level"] = "Standard GPAI Risk"

        return result

    def generate_report(self) -> str:
        """
        Generates a Markdown Conformity Assessment Report based on the evaluation.
        """
        eval_result = self.evaluate()

        report = f"# EU AI Act Conformity Assessment Report\n\n"
        report += f"**System Name:** {self.name}\n"
        report += f"**Description:** {self.description}\n"
        report += f"**Risk Level Classification:** {eval_result['risk_level']}\n\n"

        report += "## 1. Prohibited AI Practices (Article 5)\n"
        if eval_result["is_prohibited"]:
            report += "⚠️ **UNACCEPTABLE RISK: THIS SYSTEM IS BANNED.**\n"
            report += "Matching Prohibited Categories:\n"
            for reason in eval_result["prohibited_reasons"]:
                report += f"- {reason}\n"
            return report # Stop generating report if prohibited
        else:
            report += "✅ No prohibited practices detected.\n\n"

        report += "## 2. High-Risk AI Systems (Article 6 & Annex III)\n"
        if eval_result["high_risk_categories"]:
            report += "The system falls under the following High-Risk categories:\n"
            for cat in eval_result["high_risk_categories"]:
                report += f"- {cat}\n"

            if eval_result["high_risk_exceptions_applied"]:
                report += "\n**Exceptions Evaluated (Article 6.3):**\n"
                for exc in eval_result["high_risk_exceptions_applied"]:
                    report += f"- {exc}\n"

                if eval_result["is_high_risk"]:
                    report += "⚠️ Exceptions were overridden (e.g., due to profiling).\n"
                else:
                    report += "✅ Exceptions apply. System is NOT classified as High-Risk.\n"
        else:
             report += "✅ System does not fall under High-Risk Annex III categories.\n"

        report += "\n**Conformity Assessment Required:** " + ("YES" if eval_result["requires_conformity_assessment"] else "NO") + "\n"
        report += "**CE Marking Required:** " + ("YES" if eval_result["requires_ce_marking"] else "NO") + "\n\n"

        report += "## 3. Transparency Obligations (Article 50)\n"
        if eval_result["transparency_obligations"]:
            report += "The system has the following transparency obligations:\n"
            for obs in eval_result["transparency_obligations"]:
                report += f"- {obs}\n"
        else:
            report += "No specific Article 50 transparency obligations detected.\n"
        report += "\n"

        report += "## 4. General Purpose AI (GPAI) Models (Article 51-55)\n"
        if eval_result["gpai_obligations"]:
            report += "The system is classified as a GPAI model with the following obligations:\n"
            for obs in eval_result["gpai_obligations"]:
                report += f"- {obs}\n"
        else:
            report += "Not classified as a GPAI model.\n"

        return report
