"""Nodes for the bounded planner -> tool -> response workflow."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import json
import re
import time
from typing import Any

from app.agents.analysis_agent import analysis_agent
from app.agents.browser_agent import browser_agent
from app.agents.calculator_agent import calculator_agent
from app.agents.contracts import error, success
from app.agents.knowledge_agent import knowledge_agent
from app.agents.mail_agent import mail_agent
from app.agents.payment_agent import payment_agent
from app.agents.planner_agent import PlannerAgent, planner_agent
from app.agents.response_generator import ResponseGenerator, response_generator
from app.agents.sql_agent import sql_agent
from app.graph.state import RetailState
from app.logging_config import get_logger
from app.schemas.router_response import RouterResponse


ToolExecutor = Callable[[str], dict[str, Any]]
logger = get_logger(__name__)


def _mail_from_question(_: str) -> dict[str, Any]:
    # Sending mail is intentionally blocked until structured recipient/content
    # fields exist in the API. This prevents accidental delivery from prose.
    return error(
        "mail",
        "Please provide the recipient, subject, and complete email body before sending an email.",
    ).to_dict()


def _calculator_from_question(question: str) -> dict[str, Any]:
    """Translate common calculator requests into the expression-only tool input."""
    text = question.lower().replace(",", "").strip().rstrip("?.")
    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s+lakh", text)
    if lakh_match:
        text = text.replace(lakh_match.group(0), str(float(lakh_match.group(1)) * 100_000))

    percent_of = re.search(r"(\d+(?:\.\d+)?)%\s+of\s+(\d+(?:\.\d+)?)", text)
    if percent_of:
        return calculator_agent.invoke(f"{percent_of.group(1)} / 100 * {percent_of.group(2)}")

    change = re.search(r"(\d+(?:\.\d+)?)%\s+(increase|decrease|discount)\s+on\s+(\d+(?:\.\d+)?)", text)
    if change:
        rate, operation, amount = change.groups()
        operator = "+" if operation == "increase" else "-"
        return calculator_agent.invoke(f"{amount} * (1 {operator} {rate} / 100)")

    expression = text.replace("what is", "").replace("calculate", "")
    expression = expression.replace("multiplied by", "*").replace("times", "*")
    expression = expression.replace("divided by", "/").replace("plus", "+").replace("minus", "-")
    return calculator_agent.invoke(expression.strip())


# This is the single registered top-level tool set. Agent internals remain opaque.
DEFAULT_TOOL_REGISTRY: dict[str, ToolExecutor] = {
    "sql": sql_agent.invoke,
    "analysis": analysis_agent.invoke,
    "rag": knowledge_agent.invoke,
    "browser": browser_agent.invoke,
    "calculator": _calculator_from_question,
    "mail": _mail_from_question,
    "payment": payment_agent.invoke,
}

_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def _validated_result(raw: Any, expected_tool: str) -> dict[str, Any]:
    """Validate every agent output before it reaches the response generator."""
    if not isinstance(raw, dict):
        return error(expected_tool, "The selected tool returned an invalid result.").to_dict()

    required = {"status", "tool", "data", "summary", "error", "metadata"}
    if required - raw.keys() or raw.get("status") not in {"success", "error"}:
        return error(expected_tool, "The selected tool returned an invalid result.").to_dict()
    if raw.get("tool") != expected_tool:
        return error(expected_tool, "The selected tool returned an invalid result.").to_dict()
    if not isinstance(raw.get("summary"), str) or not isinstance(raw.get("metadata"), dict):
        return error(expected_tool, "The selected tool returned an invalid result.").to_dict()
    if raw["status"] == "error" and not isinstance(raw.get("error"), str):
        return error(expected_tool, "The selected tool returned an invalid result.").to_dict()
    return raw


def create_planner_node(planner: PlannerAgent = planner_agent):
    def planner_node(state: RetailState) -> dict:
        return {"decision": planner.invoke(state["question"])}

    return planner_node


def create_tool_node(tool_registry: Mapping[str, ToolExecutor] = DEFAULT_TOOL_REGISTRY):
    """Execute one primary tool and only a tightly constrained mail follow-up."""
    def tool_node(state: RetailState) -> dict:
        started = time.perf_counter()
        decision: RouterResponse = state["decision"]
        if decision.workflow == "chat":
            result = {
                "tool_result": {
                    "status": "success",
                    "tool": "chat",
                    "data": None,
                    "summary": decision.reason,
                    "error": None,
                    "metadata": {"tool_executed": False},
                }
            }
            logger.info("tool_skipped workflow=chat duration_ms=%d", (time.perf_counter() - started) * 1000)
            return result

        executor = tool_registry.get(decision.workflow)
        if executor is None:
            result = {"tool_result": {
                "status": "error",
                "tool": decision.workflow,
                "data": None,
                "summary": "",
                "error": "No suitable tool is available.",
                "metadata": {},
            }}
            logger.warning("tool_unavailable workflow=%s", decision.workflow)
            return result

        try:
            raw = _execute_with_planned_input(decision, executor, state["question"])
        except Exception:
            raw = error(decision.workflow, "The selected tool could not complete the request.").to_dict()
        primary = _validated_result(raw, decision.workflow)
        result = _run_controlled_followup(decision, state["question"], primary)
        result["metadata"] = {**result["metadata"], "latency_ms": round((time.perf_counter() - started) * 1000, 2)}
        logger.info("tool_completed tool=%s status=%s duration_ms=%s", result["tool"], result["status"], result["metadata"]["latency_ms"])
        return {"tool_result": result}

    return tool_node


def _execute_with_planned_input(
    decision: RouterResponse, executor: ToolExecutor, original_question: str
) -> dict[str, Any]:
    """Use planner-extracted input; preserve a safe legacy fallback for old plans."""
    tool_input = decision.tool_input
    if decision.workflow == "mail":
        required = ("recipient", "subject", "body")
        if not all(isinstance(tool_input.get(field), str) and tool_input[field].strip() for field in required):
            return error("mail", "Please provide the recipient, subject, and complete email body before sending an email.").to_dict()
        return mail_agent.invoke(tool_input["recipient"], tool_input["subject"], tool_input["body"])

    if decision.workflow == "calculator" and isinstance(tool_input.get("expression"), str):
        return calculator_agent.invoke(tool_input["expression"])

    question = tool_input.get("question")
    return executor(question if isinstance(question, str) and question.strip() else original_question)


def _run_controlled_followup(
    decision: RouterResponse, question: str, primary: dict[str, Any]
) -> dict[str, Any]:
    """Allow only an explicit, fully-addressed report-email after a successful result."""
    if decision.followup is None:
        return primary

    allowed = decision.workflow in {"sql", "analysis"} and decision.followup == "mail"
    recipient = _EMAIL_PATTERN.search(question)
    if not allowed or primary["status"] != "success" or recipient is None:
        primary["metadata"] = {
            **primary["metadata"],
            "followup_skipped": "A follow-up email needs an explicit recipient address and a successful primary result.",
        }
        return primary

    body = "RetailAI report\n\n" + (primary["summary"] or json.dumps(primary["data"], default=str))
    followup = _validated_result(
        mail_agent.invoke(recipient.group(0), "RetailAI requested report", body), "mail"
    )
    if followup["status"] == "error":
        followup["metadata"] = {**followup["metadata"], "primary_result": primary}
        return followup
    return {
        "status": "success",
        "tool": "mail",
        "data": {"primary": primary["data"], "followup": followup["data"]},
        "summary": " ".join(part for part in (primary["summary"], followup["summary"]) if part),
        "error": None,
        "metadata": {"primary_tool": primary["tool"], "followup_executed": "mail"},
    }


def create_response_node(responder: ResponseGenerator = response_generator):
    def response_node(state: RetailState) -> dict:
        decision: RouterResponse = state["decision"]
        return {
            "answer": responder.invoke(
                question=state["question"],
                result=state["tool_result"],
                workflow=decision.workflow,
                needs_clarification=decision.needs_clarification,
            )
        }

    return response_node
