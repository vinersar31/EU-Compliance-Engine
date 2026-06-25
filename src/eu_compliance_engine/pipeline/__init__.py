"""Event-driven EU Compliance Pipeline (GCP + ADK-style multi-agent).

Adapts the Google Cloud ``contract-compliance-pipeline`` ADK pattern to evaluate
AI technical documentation (Model Cards, System Specs) against the EU AI Act and
GDPR. See :mod:`eu_compliance_engine.pipeline.main_pipeline` for the orchestrator.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from eu_compliance_engine.pipeline.config import PipelineConfig, config
from eu_compliance_engine.pipeline.schemas import (
    AuditRecord,
    ComplianceStatus,
    ComplianceViolation,
    ExtractedTechnicalData,
    GapAnalysisReport,
    Severity,
)

if TYPE_CHECKING:  # import only for type-checkers, not at runtime
    from eu_compliance_engine.pipeline.main_pipeline import (
        CompliancePipeline,
        handle_gcs_event,
    )

__all__ = [
    "PipelineConfig",
    "config",
    "CompliancePipeline",
    "handle_gcs_event",
    "AuditRecord",
    "ComplianceStatus",
    "ComplianceViolation",
    "ExtractedTechnicalData",
    "GapAnalysisReport",
    "Severity",
]

# Lazily expose the orchestrator symbols. Importing ``main_pipeline`` eagerly
# here would re-import the module that is also run via
# ``python -m eu_compliance_engine.pipeline.main_pipeline``, triggering a runpy
# RuntimeWarning. PEP 562 ``__getattr__`` defers that import until first use.
_LAZY_EXPORTS = {"CompliancePipeline", "handle_gcs_event"}


def __getattr__(name: str) -> Any:
    if name in _LAZY_EXPORTS:
        from eu_compliance_engine.pipeline import main_pipeline

        return getattr(main_pipeline, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
