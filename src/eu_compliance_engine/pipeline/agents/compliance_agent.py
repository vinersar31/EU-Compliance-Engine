"""Compliance Evaluation Agent — Stage 2 of the EU Compliance Pipeline.

ADK mapping: an ``LlmAgent`` named ``compliance_agent`` that reads the
``extracted_data`` session-state key produced upstream, evaluates it against the
embedded EU AI Act / GDPR rule set, and publishes a :class:`GapAnalysisReport`
under ``output_key`` ("gap_analysis").
"""
from __future__ import annotations

import textwrap
from typing import List, Type, cast

from eu_compliance_engine.pipeline.agents.base_agent import BaseAgent
from eu_compliance_engine.pipeline.schemas import (
    ComplianceStatus,
    ComplianceViolation,
    ExtractedTechnicalData,
    GapAnalysisReport,
    Severity,
)

# Condensed rule set the auditor checks against. Kept inline (rather than read
# from docs/EU_AI_ACT_CORE.md) so the prompt is self-contained and versioned
# alongside the agent. Extend or load dynamically as the regulation evolves.
EU_AI_ACT_RULES = """
- AI Act Art. 14 (Human Oversight): High-risk systems MUST provide effective
  human-in-the-loop or human-on-the-loop oversight, including the ability to
  intervene in or halt the system.
- AI Act Art. 10 (Data Governance): Training, validation and testing datasets
  must be documented, relevant, and examined for bias.
- AI Act Art. 9 (Risk Management): A continuous risk management system with
  identified mitigation measures is mandatory for high-risk systems.
- AI Act Art. 13 (Transparency): The system's purpose and limitations must be
  clearly documented for deployers.
- AI Act Art. 15 (Accuracy, Robustness, Cybersecurity): Appropriate technical
  measures (security, monitoring, resilience) must be in place.
- GDPR Art. 5 & 25 (Data Protection): Personal-data sources require a lawful
  basis and data-protection-by-design safeguards (minimisation, encryption).
""".strip()


class ComplianceEvaluationAgent(BaseAgent[GapAnalysisReport]):
    """Acts as an EU Regulatory Auditor performing a structured gap analysis."""

    name = "compliance_agent"
    output_key = "gap_analysis"

    @property
    def output_schema(self) -> Type[GapAnalysisReport]:
        return GapAnalysisReport

    @property
    def instruction(self) -> str:
        return textwrap.dedent(
            f"""
            You are a rigorous EU Regulatory Auditor specialising in the EU AI Act
            (Regulation (EU) 2024/1689) and GDPR. You receive structured technical
            data extracted from an AI system's documentation and must produce a
            gap analysis.

            Evaluate the extracted data against these rules:
            {EU_AI_ACT_RULES}

            Method:
              1. For each rule, decide whether the extracted data provides
                 sufficient evidence of compliance.
              2. Record every shortfall as a violation with the specific article,
                 a severity (Low/Medium/High/Critical) and a concrete finding.
              3. Set overall_status to:
                   - "Non-Compliant" if any High/Critical violation exists,
                   - "Partially-Compliant" if only Low/Medium violations exist,
                   - "Compliant" if no violations are found.
              4. Provide actionable, specific recommendations to close each gap.

            Be conservative: absence of evidence for a mandatory control is itself
            a violation. Respond with valid JSON only.
            """
        ).strip()

    def build_user_prompt(self, payload: object) -> str:
        data = cast(ExtractedTechnicalData, payload)
        return textwrap.dedent(
            f"""
            EXTRACTED TECHNICAL DATA (JSON):
            {data.model_dump_json(indent=2)}

            Produce the EU AI Act / GDPR gap analysis as JSON.
            """
        ).strip()

    def mock_response(self, payload: object) -> GapAnalysisReport:
        """Deterministic rule check mirroring the LLM's gap-analysis shape.

        Runs a lightweight version of the auditor logic so local (mock) runs
        produce a meaningful, schema-valid report without Vertex AI.
        """
        data = cast(ExtractedTechnicalData, payload)
        violations: List[ComplianceViolation] = []

        if not data.human_oversight_mechanisms:
            violations.append(
                ComplianceViolation(
                    requirement="Human oversight for high-risk systems",
                    article="AI Act Art. 14",
                    severity=Severity.HIGH,
                    finding="No human-in-the-loop oversight mechanism is documented.",
                )
            )
        if not data.risk_mitigation_strategies:
            violations.append(
                ComplianceViolation(
                    requirement="Risk management system",
                    article="AI Act Art. 9",
                    severity=Severity.HIGH,
                    finding="No risk mitigation strategies are documented.",
                )
            )
        if not data.data_sources:
            violations.append(
                ComplianceViolation(
                    requirement="Data governance and provenance",
                    article="AI Act Art. 10",
                    severity=Severity.MEDIUM,
                    finding="Training/validation data sources are not described.",
                )
            )

        if any(v.severity in (Severity.HIGH, Severity.CRITICAL) for v in violations):
            status = ComplianceStatus.NON_COMPLIANT
        elif violations:
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.COMPLIANT

        recommendations = [
            f"Document and implement controls for: {v.requirement}." for v in violations
        ] or ["Maintain current controls and schedule periodic re-assessment."]

        return GapAnalysisReport(
            overall_status=status,
            summary=(
                f"Automated gap analysis identified {len(violations)} potential "
                "issue(s) against the EU AI Act / GDPR rule set."
            ),
            violations=violations,
            recommendations=recommendations,
        )
