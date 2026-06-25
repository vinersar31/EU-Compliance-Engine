"""Shared, dependency-free utilities for the EU Compliance Pipeline.

These helpers are framework-agnostic so they can be reused by both the ADK-style
agents (LLM calls) and the GCP integration clients (Document AI, BigQuery).

ADK mapping
-----------
In the canonical ADK ``contract-compliance-pipeline`` sample, retries and
structured-output parsing are handled implicitly by the ``Runner`` and the model
layer. Here we provide lightweight, dependency-free equivalents so the scaffold
runs locally without the full ADK runtime while remaining production-grade.
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Substrings commonly present in transient / rate-limit errors raised by the
# Vertex AI and Google Cloud client libraries (HTTP 429 / gRPC RESOURCE_EXHAUSTED
# and 5xx). Used as a best-effort fallback when no status code is exposed.
_RETRYABLE_MARKERS = (
    "429",
    "resource_exhausted",
    "resourceexhausted",
    "rate limit",
    "rate-limit",
    "quota",
    "deadline",
    "unavailable",
    "503",
    "500",
    "temporarily",
)

_RETRYABLE_TYPE_MARKERS = (
    "resourceexhausted",
    "serviceunavailable",
    "deadlineexceeded",
    "internalservererror",
    "toomanyrequests",
)


def is_retryable_error(exc: BaseException) -> bool:
    """Best-effort classification of transient errors worth retrying.

    We deliberately avoid a hard dependency on
    ``google.api_core.exceptions`` so the scaffold imports cleanly even when the
    GCP libraries are not installed. Detection inspects, in order:

    1. An explicit gRPC/HTTP status code attribute (``code``/``status_code``).
    2. The exception's type name.
    3. The stringified message.
    """
    for attr in ("code", "status_code", "grpc_status_code"):
        value = getattr(exc, attr, None)
        # gRPC StatusCode exposes the numeric code via ``.value``.
        code = getattr(value, "value", value)
        if code in (429, 500, 503):
            return True

    type_name = type(exc).__name__.lower()
    if any(marker in type_name for marker in _RETRYABLE_TYPE_MARKERS):
        return True

    message = str(exc).lower()
    return any(marker in message for marker in _RETRYABLE_MARKERS)


def async_retry(
    *,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retry_on: Callable[[BaseException], bool] = is_retryable_error,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator adding exponential backoff + jitter to an async function.

    Mirrors the implicit retry behaviour of the ADK ``Runner`` / Vertex AI model
    client, scoped to a single coroutine so individual agent and GCP calls stay
    resilient to rate limits (HTTP 429) and transient 5xx errors without failing
    the whole pipeline.
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            while True:
                attempt += 1
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001 - re-raised below
                    if attempt >= max_attempts or not retry_on(exc):
                        logger.error(
                            "%s failed after %d attempt(s): %s",
                            func.__name__,
                            attempt,
                            exc,
                        )
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += random.uniform(0, delay * 0.25)  # jitter
                    logger.warning(
                        "%s transient error on attempt %d/%d (%s). Retrying in %.1fs",
                        func.__name__,
                        attempt,
                        max_attempts,
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


def parse_json_response(raw_text: str) -> dict[str, Any]:
    """Robustly parse a JSON object from an LLM response.

    Handles the common failure modes of structured-output prompting:
      * Markdown code fences (```json ... ```)
      * Leading/trailing prose around the JSON object

    Raises ``ValueError`` (never a raw ``JSONDecodeError``) so callers can surface
    a clear, structured error.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response from model; expected a JSON object.")

    text = raw_text.strip()

    # Strip Markdown fences if the model ignored the response_mime_type hint.
    if text.startswith("```"):
        text = text[3:]
        if text[:4].lower() == "json":
            text = text[4:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fall back to extracting the outermost JSON object.
        start, end = text.find("{"), text.rfind("}")
        if 0 <= start < end:
            return json.loads(text[start : end + 1])
        raise ValueError(
            f"Could not parse JSON object from model response: {raw_text[:200]!r}"
        )
