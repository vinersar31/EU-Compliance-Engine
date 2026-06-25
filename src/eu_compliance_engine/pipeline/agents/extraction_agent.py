"""Extraction Agent — Stage 1 of the EU Compliance Pipeline.

ADK mapping: an ``LlmAgent`` named ``extraction_agent`` whose ``output_schema``
is :class:`ExtractedTechnicalData` and whose ``output_key`` ("extracted_data")
publishes the structured entities into session state for the Compliance Agent to
consume downstream.
"""
from __future__ import annotations

import textwrap
from typing import Type, cast

from eu_compliance_engine.pipeline.agents.base_agent import BaseAgent
from eu_compliance_engine.pipeline.schemas import DocumentPayload, ExtractedTechnicalData


class ExtractionAgent(BaseAgent[ExtractedTechnicalData]):
    """Acts as a Technical Data Extractor over raw Document AI output."""

    name = "extraction_agent"
    output_key = "extracted_data"

    @property
    def output_schema(self) -> Type[ExtractedTechnicalData]:
        return ExtractedTechnicalData

    @property
    def instruction(self) -> str:
        return textwrap.dedent(
            """
            You are a meticulous Technical Data Extractor specialising in AI
            system documentation (Model Cards, System Specifications, Datasheets).

            Your task: read the supplied technical document and extract ONLY the
            facts present in the text into the required JSON schema. Do not infer,
            embellish, or add compliance opinions - that is a downstream concern.

            Extract these entity groups:
              * system_purpose: the system's intended purpose and scope.
              * data_sources: every dataset / data origin mentioned.
              * human_oversight_mechanisms: any human-in-the-loop / on-the-loop
                controls, review steps, override or kill-switch mechanisms.
              * risk_mitigation_strategies: technical and organisational measures
                that reduce risk (bias testing, security, monitoring, etc.).

            If a field is not addressed in the document, return an empty list (or
            an empty string for system_purpose). Respond with valid JSON only.
            """
        ).strip()

    def build_user_prompt(self, payload: object) -> str:
        doc = cast(DocumentPayload, payload)
        return textwrap.dedent(
            f"""
            SOURCE_URI: {doc.source_uri}
            PAGE_COUNT: {doc.page_count}

            DOCUMENT TEXT:
            ---
            {doc.text}
            ---
            Extract the technical entities into the required JSON schema.
            """
        ).strip()

    def mock_response(self, payload: object) -> ExtractedTechnicalData:
        """Deterministic stand-in so the pipeline runs end-to-end without Vertex AI."""
        doc = cast(DocumentPayload, payload)
        return ExtractedTechnicalData(
            system_purpose=(
                "Automated CV screening system that ranks job applicants for "
                "recruitment shortlisting."
            ),
            data_sources=[
                "Historical applicant tracking system (ATS) records",
                "Public professional profile data",
            ],
            human_oversight_mechanisms=[
                "Recruiter reviews the top-ranked shortlist before any decision",
            ],
            risk_mitigation_strategies=[
                "Quarterly bias audit across protected attributes",
                "Encryption of candidate data at rest and in transit",
            ],
            source_uri=doc.source_uri,
        )
