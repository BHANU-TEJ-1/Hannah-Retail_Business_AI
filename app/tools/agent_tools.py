"""Approved specialized-agent capabilities for the top-level graph pipeline.

Every tool returns a JSON string of a ``ToolResult`` dict so the calling node
can deserialise it reliably regardless of which tool was routed to.
"""

import time
import json

from langchain_core.tools import tool

from app.agents.browser_agent import browser_agent
from app.agents.analysis_agent import analysis_agent
from app.agents.calculator_agent import calculator_agent
from app.agents.knowledge_agent import knowledge_agent
from app.agents.mail_agent import mail_agent
from app.agents.payment_agent import payment_agent
from app.agents.sql_agent import sql_agent
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)


def _invoke_agent(name: str, callback) -> str:
    """Run *callback*, wrap its ToolResult dict in JSON, and handle failures."""
    started = time.perf_counter()
    try:
        result = callback()
        logger.info(
            "tool_finished tool=%s status=%s duration_ms=%d",
            name,
            result.get("status"),
            (time.perf_counter() - started) * 1000,
        )
        return json.dumps(result, default=str)
    except Exception as error:
        log_failure(logger, name, error)
        return json.dumps({
            "status": "error",
            "tool": name.removesuffix("_tool"),
            "error": user_friendly_error(error, "The requested tool"),
        }, default=str)


@tool
def analysis_tool(question: str) -> str:
    """Answer analytical business questions using Pandas and company data.

    Use for revenue, profit, KPIs, sales trends, growth, top products, top
    customers, inventory analysis, and executive summaries. Do not use for raw
    operational records, policies, or live internet information.
    """
    return _invoke_agent("analysis_tool", lambda: analysis_agent.invoke(question))


@tool
def sql_tool(question: str) -> str:
    """Answer questions about internal business data.

    Use for products, inventory, sales, customers, suppliers, revenue,
    quantities, and business metrics stored in the company database.
    The capability is read-only and cannot change database data.
    """
    return _invoke_agent("sql_tool", lambda: sql_agent.invoke(question))


@tool
def rag_tool(question: str) -> str:
    """Answer questions from the internal company handbook and documentation.

    Use for policies, procedures, business definitions, reorder rules,
    payment-collection guidance, and other internal knowledge.
    """
    return _invoke_agent("rag_tool", lambda: knowledge_agent.invoke(question))


@tool
def browser_tool(question: str) -> str:
    """Research current external information on the web.

    Use for latest news, upcoming holidays, current events, market trends,
    and external business research that cannot come from internal data.
    """
    return _invoke_agent("browser_tool", lambda: browser_agent.invoke(question))


@tool
def calculator_tool(expression: str) -> str:
    """Calculate a mathematical expression accurately.

    Use for arithmetic, percentages, totals, ratios, and other calculations.
    Accept only the planner-extracted expression, such as `1250 * 18`; never
    access business data or perform analysis.
    """
    return _invoke_agent("calculator_tool", lambda: calculator_agent.invoke(expression))


@tool
def mail_tool(recipient: str, subject: str, body: str) -> str:
    """Send an email through the company's mail capability.

    Use only when the user explicitly asks to send an email and the recipient,
    subject, and complete email body are supplied as structured input. Never
    parse English, select recipients, or invent content. Do not use for drafting.
    """
    def run() -> dict:
        return mail_agent.invoke(recipient, subject, body)
    return _invoke_agent("mail_tool", run)


@tool
def payment_tool(question: str) -> str:
    """Run the payment-collections capability for unpaid customer balances.

    Use only when the user explicitly asks to send payment reminders for unpaid
    bills. It identifies balances from internal data and sends reminders.
    """
    return _invoke_agent("payment_tool", lambda: payment_agent.invoke(question))


# The full tool registry the planner can route to.
agent_tools = [
    analysis_tool,
    sql_tool,
    rag_tool,
    browser_tool,
    calculator_tool,
    mail_tool,
    payment_tool,
]
