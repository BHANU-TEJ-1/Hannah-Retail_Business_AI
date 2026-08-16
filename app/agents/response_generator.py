"""The single top-level response generator for all RetailAI tool results."""

from __future__ import annotations

import json
import time
from typing import Any

from app.llm.llm_factory import llm_factory
from app.prompts.response_prompt import build_response_prompt
from app.schemas.response import Response
from app.logging_config import get_logger


logger = get_logger(__name__)


class ResponseGenerator:
    """Translate a validated tool result into a concise user-facing answer."""

    def __init__(self, llm=None) -> None:
        model = llm or llm_factory.get_response_generator()
        self._responder = model.with_structured_output(Response)

    def invoke(
        self,
        question: str,
        result: dict[str, Any],
        workflow: str,
        needs_clarification: bool = False,
    ) -> str:
        """Generate an answer, with a safe deterministic fallback on failure."""
        # These paths contain no tool data to interpret. Avoid a provider call
        # while preserving an actionable, user-safe answer.
        if result.get("status") == "error":
            return result.get("error") or "I could not complete that request."
        if workflow == "chat":
            if needs_clarification:
                return "Could you clarify what you would like to know or do?"
            return "Hello! I can help with retail data, analysis, policies, research, and calculations."

        prompt = build_response_prompt(
            question=question,
            workflow=workflow,
            result=json.dumps(result, default=str),
            needs_clarification=needs_clarification,
        )
        try:
            started = time.perf_counter()
            response = self._responder.invoke(prompt)
            if not isinstance(response, Response):
                response = Response.model_validate(response)
            answer = response.answer.strip()
            logger.info("response_generated workflow=%s duration_ms=%d", workflow, (time.perf_counter() - started) * 1000)
            return answer
        except Exception as error:
            logger.warning("response_generation_fallback workflow=%s error_type=%s", workflow, type(error).__name__)
            # Tool errors and summaries are already user-safe by the common contract.
            return result.get("summary") or "I completed your request."


response_generator = ResponseGenerator()
