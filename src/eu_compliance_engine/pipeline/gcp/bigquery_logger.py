"""BigQuery logging — reporting stage of the pipeline.

Streams the final :class:`AuditRecord` (provenance + gap analysis) into the
``eu_compliance_audits`` table. In mock mode the row is logged locally instead of
inserted, so local runs need no BigQuery dataset.

ADK mapping: the sample persists results in a final reporting step; this client
is the equivalent sink, invoked by the orchestrator after the Compliance Agent.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

from eu_compliance_engine.pipeline.config import PipelineConfig, config as default_config
from eu_compliance_engine.pipeline.schemas import AuditRecord
from eu_compliance_engine.pipeline.utils import async_retry

logger = logging.getLogger(__name__)

try:  # pragma: no cover - import guard
    from google.cloud import bigquery
except Exception:  # pragma: no cover
    bigquery = None  # type: ignore[assignment]


class BigQueryLoggerError(RuntimeError):
    """Raised when an audit record cannot be persisted."""


class BigQueryLogger:
    """Streams audit reports into BigQuery via the streaming-insert API."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or default_config
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if bigquery is None:
            raise BigQueryLoggerError(
                "google-cloud-bigquery is not installed. Install it or run with "
                "PIPELINE_MOCK_MODE=1."
            )
        self._client = bigquery.Client(
            project=self.config.project_id, location=self.config.bq_location
        )
        return self._client

    @staticmethod
    def _to_row(record: AuditRecord) -> Dict[str, Any]:
        """Flatten the audit record into a BigQuery-friendly row.

        Nested objects are serialised to JSON columns so the table schema stays
        stable as the report model evolves, while top-level scalars remain easy
        to query / partition on.
        """
        return {
            "audit_id": record.audit_id,
            "source_uri": record.source_uri,
            "created_at": record.created_at,
            "model": record.model,
            "overall_status": record.report.overall_status.value,
            "violation_count": len(record.report.violations),
            "extracted_data_json": record.extracted_data.model_dump_json(),
            "report_json": record.report.model_dump_json(),
        }

    async def stream_report(self, record: AuditRecord) -> None:
        """Insert a single audit record. Raises ``BigQueryLoggerError`` on failure."""
        row = self._to_row(record)
        if self.config.mock_mode:
            logger.info(
                "[bigquery] mock_mode -> would insert into %s: %s",
                self.config.bq_table_fqn,
                json.dumps(row)[:500],
            )
            return
        await self._insert_live(row)

    @async_retry()  # retry on BigQuery rate limits / transient errors
    async def _insert_live(self, row: Dict[str, Any]) -> None:
        client = self._get_client()
        self.config.require_gcp()
        table_id = self.config.bq_table_fqn

        def _do_insert():
            # insert_rows_json uses the streaming API and *returns* per-row errors
            # rather than raising, so we surface them explicitly below.
            return client.insert_rows_json(table_id, [row])

        errors = await asyncio.to_thread(_do_insert)
        if errors:
            raise BigQueryLoggerError(f"BigQuery streaming insert failed: {errors}")
        logger.info("[bigquery] inserted audit %s into %s", row["audit_id"], table_id)

    def ensure_table(self) -> None:
        """Idempotently create the dataset + table (one-off provisioning helper).

        Not called on the hot path; intended for setup scripts or IaC. Kept here
        so the table schema lives next to the writer that depends on it.
        """
        if self.config.mock_mode:
            return
        client = self._get_client()
        dataset = bigquery.Dataset(f"{self.config.project_id}.{self.config.bq_dataset}")
        dataset.location = self.config.bq_location
        client.create_dataset(dataset, exists_ok=True)

        schema = [
            bigquery.SchemaField("audit_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_uri", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("model", "STRING"),
            bigquery.SchemaField("overall_status", "STRING"),
            bigquery.SchemaField("violation_count", "INTEGER"),
            bigquery.SchemaField("extracted_data_json", "JSON"),
            bigquery.SchemaField("report_json", "JSON"),
        ]
        table = bigquery.Table(self.config.bq_table_fqn, schema=schema)
        client.create_table(table, exists_ok=True)
        logger.info("[bigquery] ensured table %s", self.config.bq_table_fqn)
