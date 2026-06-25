"""Centralised configuration for the EU Compliance Pipeline.

All runtime configuration is sourced from environment variables so the exact
same code runs locally (mock mode) and on GCP (Cloud Run / Cloud Functions)
without modification.

ADK mapping
-----------
In the canonical Google ADK ``contract-compliance-pipeline`` sample this maps to
the ``.env`` file plus the ``RunConfig`` handed to the ``Runner``. Here we keep a
single immutable :class:`PipelineConfig` that every stage receives.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable, env-driven configuration shared across every pipeline stage."""

    # --- Vertex AI / Gemini -------------------------------------------------
    project_id: str = field(
        default_factory=lambda: os.environ.get("GCP_PROJECT_ID", "")
    )
    location: str = field(
        default_factory=lambda: os.environ.get("GCP_LOCATION", "europe-west4")
    )
    gemini_model: str = field(
        default_factory=lambda: os.environ.get("GEMINI_MODEL", "gemini-3.1-pro")
    )

    # --- Document AI --------------------------------------------------------
    docai_location: str = field(
        default_factory=lambda: os.environ.get("DOCAI_LOCATION", "eu")
    )
    docai_processor_id: str = field(
        default_factory=lambda: os.environ.get("DOCAI_PROCESSOR_ID", "")
    )
    docai_processor_version: str = field(
        default_factory=lambda: os.environ.get("DOCAI_PROCESSOR_VERSION", "")
    )

    # --- BigQuery -----------------------------------------------------------
    bq_dataset: str = field(
        default_factory=lambda: os.environ.get("BQ_DATASET", "eu_compliance")
    )
    bq_table: str = field(
        default_factory=lambda: os.environ.get("BQ_TABLE", "eu_compliance_audits")
    )
    bq_location: str = field(
        default_factory=lambda: os.environ.get("BQ_LOCATION", "EU")
    )

    # --- Resilience (rate-limit / transient-error backoff) ------------------
    max_retries: int = field(
        default_factory=lambda: int(os.environ.get("PIPELINE_MAX_RETRIES", "5"))
    )
    base_backoff_seconds: float = field(
        default_factory=lambda: float(os.environ.get("PIPELINE_BASE_BACKOFF", "1.0"))
    )

    # --- Local development --------------------------------------------------
    # When True the pipeline uses deterministic in-memory fakes for Document AI,
    # the Gemini agents, and BigQuery so the full Extraction -> Evaluation ->
    # Reporting flow can be exercised without GCP credentials. Defaults to True
    # whenever no GCP project is configured, so a fresh clone "just runs".
    mock_mode: bool = field(
        default_factory=lambda: _env_bool(
            "PIPELINE_MOCK_MODE", not bool(os.environ.get("GCP_PROJECT_ID"))
        )
    )

    @property
    def bq_table_fqn(self) -> str:
        """Fully-qualified BigQuery table id: ``project.dataset.table``."""
        return f"{self.project_id}.{self.bq_dataset}.{self.bq_table}"

    def require_gcp(self) -> None:
        """Validate mandatory GCP settings before any live API call.

        Raises ``ValueError`` (fail fast) when live mode is requested but the
        minimum configuration is absent.
        """
        if self.mock_mode:
            return
        if not self.project_id:
            raise ValueError(
                "GCP_PROJECT_ID is required for live mode. Set it, or enable "
                "PIPELINE_MOCK_MODE=1 for local runs."
            )


# Module-level singleton constructed from the current process environment.
# Stages accept an explicit ``config`` argument (defaulting to this) so tests can
# inject their own PipelineConfig instances.
config = PipelineConfig()
