"""ADK-style base agent for the EU Compliance Pipeline.

Mapping to the Google ADK ``contract-compliance-pipeline`` sample
-----------------------------------------------------------------
In the canonical sample, each pipeline step is a ``google.adk.agents.LlmAgent``
configured with:

    * ``name``          -> stable identifier used in traces / session state
    * ``model``         -> the Gemini model id served via Vertex AI
    * ``instruction``   -> the system prompt defining the agent's role
    * ``output_schema`` -> a Pydantic model enforcing structured output
    * ``output_key``    -> the ``session.state`` key the result is written to

``LlmAgent`` instances are composed by a ``SequentialAgent`` and executed by a
``Runner`` against a ``SessionService``. To keep this scaffold runnable without
the full ADK runtime, :class:`BaseAgent` re-implements that contract on top of
the Vertex AI ``google-genai`` SDK. Migrating to real ADK later is mechanical:
replace each ``BaseAgent`` subclass with ``LlmAgent(...)`` reusing the same
``instruction`` / ``output_schema`` values already defined here.
"""
from __future__ import annotations

import abc
import logging
from typing import Generic, Type, TypeVar

from pydantic import BaseModel, ValidationError

from eu_compliance_engine.pipeline.config import PipelineConfig, config as default_config
from eu_compliance_engine.pipeline.utils import async_retry, parse_json_response

logger = logging.getLogger(__name__)

# Lazily imported so the package imports cleanly without google-genai installed
# (e.g. mock mode / CI). The real client is only constructed for live calls.
try:  # pragma: no cover - import guard
    from google import genai
    from google.genai import types as genai_types
except Exception:  # pragma: no cover
    genai = None  # type: ignore[assignment]
    genai_types = None  # type: ignore[assignment]


TOutput = TypeVar("TOutput", bound=BaseModel)


class AgentError(RuntimeError):
    """Raised when an agent cannot produce a schema-valid result."""


class BaseAgent(abc.ABC, Generic[TOutput]):
    """Common scaffolding for a single LLM-backed pipeline stage.

    Conceptually equivalent to a configured ``google.adk.agents.LlmAgent``.
    """

    #: Stable agent identifier (ADK ``name``).
    name: str = "base_agent"
    #: ``session.state`` key under which this agent publishes (ADK ``output_key``).
    output_key: str = "result"

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or default_config
        self._client = None  # constructed lazily for live calls

    # --- Subclass contract -------------------------------------------------- #
    @property
    @abc.abstractmethod
    def instruction(self) -> str:
        """System prompt defining the agent's role (ADK ``instruction``)."""

    @property
    @abc.abstractmethod
    def output_schema(self) -> Type[TOutput]:
        """Pydantic schema enforcing structured output (ADK ``output_schema``)."""

    @abc.abstractmethod
    def build_user_prompt(self, payload: object) -> str:
        """Render the per-invocation user content from the incoming state."""

    @abc.abstractmethod
    def mock_response(self, payload: object) -> TOutput:
        """Deterministic result used when ``config.mock_mode`` is enabled."""

    # --- Vertex AI client --------------------------------------------------- #
    def _get_client(self):
        """Construct (once) a Vertex AI-backed ``google-genai`` client.

        Uses Application Default Credentials; on Cloud Run / Functions this is
        the attached service account. ``vertexai=True`` routes through the
        regional Vertex AI endpoint (IAM auth) rather than the public Gemini API
        used by the existing ``llm_evaluator`` module.
        """
        if self._client is not None:
            return self._client
        if genai is None:
            raise AgentError(
                "google-genai is not installed. Install it or run with "
                "PIPELINE_MOCK_MODE=1."
            )
        self.config.require_gcp()
        self._client = genai.Client(
            vertexai=True,
            project=self.config.project_id,
            location=self.config.location,
        )
        return self._client

    # --- Public API --------------------------------------------------------- #
    async def run(self, payload: object) -> TOutput:
        """Execute the agent and return a validated ``output_schema`` instance.

        The analogue of ``Runner.run_async`` for a single ``LlmAgent``.
        """
        if self.config.mock_mode:
            logger.info("[%s] mock_mode -> deterministic response", self.name)
            return self.mock_response(payload)
        raw = await self._generate(self.build_user_prompt(payload))
        return self._parse(raw)

    # --- Internals ---------------------------------------------------------- #
    @async_retry()  # exponential backoff for HTTP 429 / transient 5xx
    async def _generate(self, user_prompt: str) -> str:
        client = self._get_client()
        # response_schema + JSON mime type asks Vertex AI to honour our Pydantic
        # schema directly (structured output), mirroring ADK ``output_schema``.
        gen_config = genai_types.GenerateContentConfig(
            system_instruction=self.instruction,
            response_mime_type="application/json",
            response_schema=self.output_schema,
            temperature=0.0,  # deterministic auditing
        )
        logger.info("[%s] calling model %s", self.name, self.config.gemini_model)
        # The async client (`client.aio`) keeps the event loop free while the
        # Vertex AI request is in flight.
        response = await client.aio.models.generate_content(
            model=self.config.gemini_model,
            contents=user_prompt,
            config=gen_config,
        )
        text = getattr(response, "text", None)
        if not text:
            raise AgentError(f"[{self.name}] empty response from model")
        return text

    def _parse(self, raw_text: str) -> TOutput:
        try:
            data = parse_json_response(raw_text)
            return self.output_schema.model_validate(data)
        except (ValueError, ValidationError) as exc:
            # Surface a clear, structured failure rather than a raw parse error.
            raise AgentError(
                f"[{self.name}] failed to parse structured output: {exc}"
            ) from exc
