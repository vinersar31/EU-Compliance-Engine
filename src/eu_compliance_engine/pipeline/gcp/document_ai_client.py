"""Document AI integration — ingestion stage of the pipeline.

Parses a PDF (or image) stored in GCS into text + layout using a Document AI
processor. The live implementation is fully wired; ``config.mock_mode``
short-circuits to a deterministic in-memory document so the pipeline runs without
GCP credentials.

ADK mapping: in the contract-compliance sample this is a *tool* the ingestion
agent calls. Here it is a plain async client invoked by the orchestrator before
the first ``LlmAgent`` runs.
"""
from __future__ import annotations

import asyncio
import logging

from eu_compliance_engine.pipeline.config import PipelineConfig, config as default_config
from eu_compliance_engine.pipeline.schemas import DocumentPayload
from eu_compliance_engine.pipeline.utils import async_retry

logger = logging.getLogger(__name__)

# Lazy import keeps the package importable without the GCP libraries installed.
try:  # pragma: no cover - import guard
    from google.api_core.client_options import ClientOptions
    from google.cloud import documentai
except Exception:  # pragma: no cover
    documentai = None  # type: ignore[assignment]
    ClientOptions = None  # type: ignore[assignment]


# Canned document used in mock mode (a deliberately partial Model Card so the
# downstream gap analysis has something meaningful to flag).
_MOCK_DOCUMENT_TEXT = """\
Model Card: Talent-Match Recruitment Ranking System
Intended Purpose: Rank and shortlist job applicants for corporate recruiters.
Data Sources: Historical ATS records (2015-2024); public professional profiles.
Human Oversight: Recruiters review the AI-generated shortlist before contacting
candidates and may override any ranking.
Risk Mitigation: Quarterly bias audits across gender and age; data encrypted at
rest (AES-256) and in transit (TLS 1.3); continuous performance monitoring.
"""


class DocumentAIError(RuntimeError):
    """Raised when a document cannot be parsed."""


class DocumentAIClient:
    """Thin async wrapper around the Document AI online-processing API."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or default_config
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if documentai is None:
            raise DocumentAIError(
                "google-cloud-documentai is not installed. Install it or run "
                "with PIPELINE_MOCK_MODE=1."
            )
        # Document AI is regional; the endpoint must match the processor region.
        opts = ClientOptions(
            api_endpoint=f"{self.config.docai_location}-documentai.googleapis.com"
        )
        self._client = documentai.DocumentProcessorServiceClient(client_options=opts)
        return self._client

    async def process_document_from_gcs(
        self, gcs_uri: str, mime_type: str = "application/pdf"
    ) -> DocumentPayload:
        """Parse a single document located at ``gcs_uri`` (gs://...)."""
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Expected a gs:// URI, got: {gcs_uri!r}")

        if self.config.mock_mode:
            logger.info(
                "[document_ai] mock_mode -> canned document for %s", gcs_uri
            )
            return DocumentPayload(
                source_uri=gcs_uri,
                mime_type=mime_type,
                text=_MOCK_DOCUMENT_TEXT,
                page_count=1,
            )
        return await self._process_live(gcs_uri, mime_type)

    @async_retry()  # retry on Document AI rate limits / transient errors
    async def _process_live(self, gcs_uri: str, mime_type: str) -> DocumentPayload:
        client = self._get_client()
        self.config.require_gcp()
        if not self.config.docai_processor_id:
            raise DocumentAIError(
                "DOCAI_PROCESSOR_ID is required for live Document AI calls."
            )

        # Build the fully-qualified processor (or pinned version) resource name.
        if self.config.docai_processor_version:
            name = client.processor_version_path(
                self.config.project_id,
                self.config.docai_location,
                self.config.docai_processor_id,
                self.config.docai_processor_version,
            )
        else:
            name = client.processor_path(
                self.config.project_id,
                self.config.docai_location,
                self.config.docai_processor_id,
            )

        request = documentai.ProcessRequest(
            name=name,
            gcs_document=documentai.GcsDocument(gcs_uri=gcs_uri, mime_type=mime_type),
            # skip_human_review=True,  # enable for fully automated runs
        )

        # The Document AI SDK is synchronous; run it off the event loop so the
        # orchestrator can interleave other work.
        result = await asyncio.to_thread(client.process_document, request=request)
        document = result.document
        return DocumentPayload(
            source_uri=gcs_uri,
            mime_type=mime_type,
            text=document.text or "",
            page_count=len(document.pages),
        )
