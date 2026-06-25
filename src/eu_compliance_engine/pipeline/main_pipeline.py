"""EU Compliance Pipeline — asynchronous orchestrator.

Wires the event-driven flow:

    GCS object finalize (Pub/Sub / Eventarc)
        -> Document AI parse            (gcp.document_ai_client)
        -> Extraction Agent             (agents.extraction_agent)   [Stage 1]
        -> Compliance Evaluation Agent  (agents.compliance_agent)   [Stage 2]
        -> BigQuery audit log           (gcp.bigquery_logger)       [Reporting]

ADK mapping
-----------
:class:`CompliancePipeline` is the equivalent of the sample's
``SequentialAgent`` orchestrator. The typed objects handed between stages play
the role of ADK ``session.state`` (each agent's ``output_key`` is the state key).
:func:`handle_gcs_event` is the Cloud Functions / Eventarc entry point a
``Runner`` would normally be triggered by.

Run the local smoke test (mock mode, no GCP needed):

    python -m eu_compliance_engine.pipeline.main_pipeline
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import logging
import uuid
from typing import Any, Dict, Optional

from eu_compliance_engine.pipeline.agents.compliance_agent import (
    ComplianceEvaluationAgent,
)
from eu_compliance_engine.pipeline.agents.extraction_agent import ExtractionAgent
from eu_compliance_engine.pipeline.config import PipelineConfig, config as default_config
from eu_compliance_engine.pipeline.gcp.bigquery_logger import BigQueryLogger
from eu_compliance_engine.pipeline.gcp.document_ai_client import DocumentAIClient
from eu_compliance_engine.pipeline.schemas import AuditRecord, GapAnalysisReport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("eu_compliance_pipeline")

# Document types Document AI can parse; other uploads are ignored by the trigger.
_SUPPORTED_SUFFIXES = (".pdf", ".tiff", ".tif", ".png", ".jpg", ".jpeg")


class CompliancePipeline:
    """Sequential, async orchestrator coordinating ingestion, the two agents,
    and reporting.

    Construct once and reuse across events: the GCP clients and agents cache
    their underlying connections.
    """

    def __init__(self, config: Optional[PipelineConfig] = None) -> None:
        self.config = config or default_config
        # Stage components — analogous to the sub-agents of a SequentialAgent.
        self.doc_ai = DocumentAIClient(self.config)
        self.extraction_agent = ExtractionAgent(self.config)
        self.compliance_agent = ComplianceEvaluationAgent(self.config)
        self.bq_logger = BigQueryLogger(self.config)

    async def run(self, gcs_uri: str, mime_type: str = "application/pdf") -> AuditRecord:
        """Execute the full pipeline for a single document.

        State hand-off is explicit and typed: each stage's output is the next
        stage's input, mirroring how ADK writes ``output_key`` into session
        state and reads it back in the following agent.
        """
        audit_id = str(uuid.uuid4())
        logger.info("[%s] pipeline start for %s", audit_id, gcs_uri)

        # --- Ingestion: Document AI -> DocumentPayload --------------------- #
        document = await self.doc_ai.process_document_from_gcs(gcs_uri, mime_type)
        logger.info("[%s] parsed %d page(s)", audit_id, document.page_count)

        # --- Stage 1: Extraction Agent  (state['extracted_data']) --------- #
        extracted = await self.extraction_agent.run(document)
        logger.info(
            "[%s] extracted purpose=%r, %d data source(s)",
            audit_id,
            extracted.system_purpose[:60],
            len(extracted.data_sources),
        )

        # --- Stage 2: Compliance Agent  (state['gap_analysis']) ----------- #
        report: GapAnalysisReport = await self.compliance_agent.run(extracted)
        logger.info(
            "[%s] verdict=%s, %d violation(s)",
            audit_id,
            report.overall_status.value,
            len(report.violations),
        )

        # --- Reporting: persist to BigQuery ------------------------------- #
        record = AuditRecord(
            audit_id=audit_id,
            source_uri=gcs_uri,
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            model=self.config.gemini_model,
            extracted_data=extracted,
            report=report,
        )
        await self.bq_logger.stream_report(record)
        logger.info(
            "[%s] pipeline complete -> %s", audit_id, report.overall_status.value
        )
        return record


# --------------------------------------------------------------------------- #
# Event entry points (Cloud Functions / Eventarc / Pub-Sub triggers)
# --------------------------------------------------------------------------- #
def _gcs_uri_from_event(event: Dict[str, Any]) -> str:
    """Derive a gs:// URI from a GCS finalize event payload.

    Supports both the Cloud Functions GCS event shape ({'bucket', 'name'}) and a
    Pub/Sub-wrapped / Eventarc CloudEvent ({'data': {...}}).
    """
    data = event.get("data", event)
    bucket = data.get("bucket")
    name = data.get("name")
    if not bucket or not name:
        raise ValueError(f"Event missing bucket/name: {event!r}")
    return f"gs://{bucket}/{name}"


async def handle_gcs_event(
    event: Dict[str, Any], pipeline: Optional[CompliancePipeline] = None
) -> Dict[str, Any]:
    """Async handler mimicking a GCS-finalize -> Pub/Sub trigger.

    Deploy as a Cloud Function (2nd gen) / Cloud Run service subscribed to the
    bucket's object-finalize notifications. Returns a small JSON-able summary and
    never raises, so a single bad object cannot poison the subscription.
    """
    pipeline = pipeline or CompliancePipeline()
    gcs_uri = _gcs_uri_from_event(event)

    # Only process documents we can parse; ignore unrelated objects.
    if not gcs_uri.lower().endswith(_SUPPORTED_SUFFIXES):
        logger.info("ignoring non-document object: %s", gcs_uri)
        return {"status": "skipped", "source_uri": gcs_uri}

    try:
        record = await pipeline.run(gcs_uri)
    except Exception as exc:  # noqa: BLE001 - top-level boundary; never crash the trigger
        logger.exception("pipeline failed for %s", gcs_uri)
        return {"status": "error", "source_uri": gcs_uri, "error": str(exc)}

    return {
        "status": "ok",
        "audit_id": record.audit_id,
        "source_uri": record.source_uri,
        "overall_status": record.report.overall_status.value,
        "violation_count": len(record.report.violations),
    }


async def _main() -> None:
    """Local smoke test: runs the full pipeline against a sample GCS event.

    With the default (mock) configuration this exercises every stage end-to-end
    without contacting GCP.
    """
    sample_event = {"bucket": "eu-ai-docs", "name": "model_cards/talent_match_v2.pdf"}
    result = await handle_gcs_event(sample_event)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
