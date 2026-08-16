"""Planner facade that classifies a request without executing a workflow."""

import time

from app.error_messages import log_failure
from app.llm.llm_factory import llm_factory
from app.logging_config import get_logger
from app.prompts.router_prompt import build_planner_prompt
from app.schemas.router_response import RouterResponse
from app.tools.agent_tools import agent_tools


logger = get_logger(__name__)


class PlannerAgent:
    """Select exactly one workflow; this agent never has tools or business context."""

    def __init__(self, llm=None, tools=None) -> None:
        model = llm or llm_factory.get_qwen()
        self._planner = model.with_structured_output(RouterResponse)
        # Keep the planner's visible capabilities explicit and in sync with the
        # top-level wrappers. The planner receives their descriptions in its prompt.
        self.registered_tools = tuple(tools or agent_tools)
        self._workflows = {tool.name.removesuffix("_tool") for tool in self.registered_tools}

    def invoke(self, question: str) -> RouterResponse:
        started = time.perf_counter()
        if not question or not question.strip():
            logger.warning("planner_empty_query")
            return self._clarification_response("Please provide a question so I can select a workflow.")

        logger.info("planner_request query=%r", question)
        try:
            decision = self._planner.invoke(build_planner_prompt(question))
            if not isinstance(decision, RouterResponse):
                decision = RouterResponse.model_validate(decision)
            if decision.workflow != "chat" and decision.workflow not in self._workflows:
                raise ValueError("Planner selected an unregistered workflow")
            logger.info(
                "planner_decision workflow=%s followup=%s confidence=%.2f duration_ms=%d",
                decision.workflow,
                decision.followup,
                decision.confidence,
                (time.perf_counter() - started) * 1000,
            )
            return decision
        except Exception as error:
            log_failure(logger, "workflow_planning", error)
            return self._clarification_response(
                "Clarification required because workflow selection is temporarily unavailable."
            )

    @staticmethod
    def _clarification_response(reason: str) -> RouterResponse:
        """Use Chat as the safe fallback when no reliable workflow can be selected."""
        return RouterResponse(
            workflow="chat",
            confidence=0.0,
            reason=reason,
            needs_clarification=True,
            followup=None,
        )


planner_agent = PlannerAgent()
