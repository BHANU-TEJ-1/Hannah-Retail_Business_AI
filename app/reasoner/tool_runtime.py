"""Tool Runtime: exposes Phase 1/2 tools to the Reasoner and executes tool
calls. Contains no reasoning of its own - it only dispatches to the
independent tools and returns their structured results."""

import json
from concurrent.futures import ThreadPoolExecutor

from langchain_core.messages import ToolMessage

from app.rag.rag_retriever import rag_retriever
from app.tools.browser_tool import browser_tool
from app.tools.calculator_tool import calculator_tool
from app.tools.gmail_tool import gmail_tool
from app.tools.sql_executor import sql_executor as _sql_executor
from app.tools.sql_validator import sql_validator


def sql_verifier(sql: str) -> dict:
    """Check whether a SQL string is a safe, single SELECT statement.
    Always call this before sql_executor."""
    return sql_validator.invoke(sql)


def sql_executor(sql: str) -> dict:
    """Execute a verified SQL SELECT statement and return the resulting rows.
    Only call this after sql_verifier has confirmed the SQL is safe."""
    return _sql_executor.invoke(sql)


def calculator(expression: str) -> dict:
    """Evaluate a deterministic arithmetic expression, e.g. '25 + 18' or
    '20% of 150'."""
    return calculator_tool.invoke(expression)


def browser(query: str) -> dict:
    """Search the public web for current information not available in the
    database or company handbook."""
    return browser_tool.invoke(query)


def mail(recipient: str, subject: str, body: str) -> dict:
    """Send an email to a single recipient with the given subject and body."""
    return gmail_tool.invoke(recipient, subject, body)


def rag(query: str) -> dict:
    """Search the company handbook for policies, procedures, and business
    documentation."""
    return rag_retriever.invoke(query)


# Every tool the Reasoner is allowed to call.
TOOLS = [sql_verifier, sql_executor, calculator, browser, mail, rag]
TOOL_REGISTRY = {function.__name__: function for function in TOOLS}


class ToolRuntime:
    """Runs the tool calls requested by the Reasoner. Independent calls in
    the same turn run in parallel; results are returned as ToolMessages in
    the same order the Reasoner requested them."""

    def __init__(self, registry: dict | None = None):
        self._registry = registry or TOOL_REGISTRY

    def run(self, tool_calls: list[dict]) -> list[ToolMessage]:
        if len(tool_calls) == 1:
            return [self._run_one(tool_calls[0])]

        with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
            futures = [executor.submit(self._run_one, call) for call in tool_calls]
            return [future.result() for future in futures]

    def _run_one(self, tool_call: dict) -> ToolMessage:
        name = tool_call["name"]
        arguments = tool_call.get("args", {})
        call_id = tool_call.get("id")

        function = self._registry.get(name)

        if function is None:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        else:
            try:
                result = function(**arguments)
            except Exception as error:
                result = {"success": False, "error": f"Tool '{name}' failed: {error}"}

        return ToolMessage(content=json.dumps(result), tool_call_id=call_id, name=name)


tool_runtime = ToolRuntime()
