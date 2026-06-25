"""Typed contracts handed between pipeline stages.

These Pydantic models play the same role as the ``output_schema`` models in the
Google ADK ``contract-compliance-pipeline`` sample: each is passed to Gemini as
the structured-output schema AND used to validate the parsed response, giving
every agent a strict, machine-checkable contract.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Stage 0 — Ingestion (Document AI output)
# --------------------------------------------------------------------------- #
class DocumentPayload(BaseModel):
    """Raw text + lightweight layout extracted from a source document.

    Mirrors the subset of the Document AI ``Document`` proto the downstream
    agents need. Produced by ``gcp.document_ai_client.DocumentAIClient`` and
    consumed by the Extraction Agent.
    """

    source_uri: str = Field(
        ..., description="GCS URI of the source document, e.g. gs://bucket/model_card.pdf"
    )
    mime_type: str = Field(
        default="application/pdf", description="MIME type reported by Document AI"
    )
    text: str = Field(..., description="Full concatenated document text")
    page_count: int = Field(
        default=0, ge=0, description="Number of pages parsed by Document AI"
    )


# --------------------------------------------------------------------------- #
# Stage 1 — Extraction Agent output
# --------------------------------------------------------------------------- #
class ExtractedTechnicalData(BaseModel):
    """Strict schema the Extraction Agent must populate from the document.

    Maps directly to the four entity groups required to assess EU AI Act
    technical documentation (Annex IV).
    """

    system_purpose: str = Field(
        ..., description="The intended purpose and functional scope of the AI system"
    )
    data_sources: List[str] = Field(
        default_factory=list,
        description="Datasets / data origins used for training, testing and operation",
    )
    human_oversight_mechanisms: List[str] = Field(
        default_factory=list,
        description="Human-in-the-loop / on-the-loop controls described in the document",
    )
    risk_mitigation_strategies: List[str] = Field(
        default_factory=list,
        description="Technical and organisational measures mitigating identified risks",
    )
    source_uri: Optional[str] = Field(
        default=None, description="GCS URI carried through for traceability"
    )


# --------------------------------------------------------------------------- #
# Stage 2 — Compliance Evaluation Agent output
# --------------------------------------------------------------------------- #
class ComplianceStatus(str, Enum):
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PARTIALLY_COMPLIANT = "Partially-Compliant"


class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ComplianceViolation(BaseModel):
    requirement: str = Field(
        ..., description="The EU AI Act / GDPR requirement that is not satisfied"
    )
    article: Optional[str] = Field(
        default=None, description="Specific article reference, e.g. 'AI Act Art. 14'"
    )
    severity: Severity = Field(
        default=Severity.MEDIUM, description="Assessed severity of the gap"
    )
    finding: str = Field(
        ..., description="Why the extracted documentation fails to meet the requirement"
    )


class GapAnalysisReport(BaseModel):
    """Final structured audit report emitted by the Compliance Agent.

    This is the payload streamed into the ``eu_compliance_audits`` BigQuery table.
    """

    overall_status: ComplianceStatus = Field(
        ..., description="Overall compliance verdict"
    )
    summary: str = Field(
        ..., description="One-paragraph executive summary of the assessment"
    )
    violations: List[ComplianceViolation] = Field(
        default_factory=list, description="Missing or insufficient requirements"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Actionable remediation steps"
    )


# --------------------------------------------------------------------------- #
# Pipeline envelope (persisted record)
# --------------------------------------------------------------------------- #
class AuditRecord(BaseModel):
    """Row persisted to BigQuery: joins provenance with the gap analysis."""

    audit_id: str = Field(..., description="Unique id for this audit run (uuid4)")
    source_uri: str = Field(..., description="GCS URI of the evaluated document")
    created_at: str = Field(..., description="ISO-8601 UTC timestamp of the audit")
    model: str = Field(..., description="Gemini model used for evaluation")
    extracted_data: ExtractedTechnicalData
    report: GapAnalysisReport
