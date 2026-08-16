"""Tests the Reasoner's tool-calling loop with a scripted fake LLM, so no
real network call to OpenRouter/DeepSeek is made. The underlying Phase 1/2
tools are mocked at their source so no DB, SMTP, or web call happens either.
"""

from unittest.mock import patch

from langchain_core.messages import AIMessage

from app.reasoner.reasoner import Reasoner
from app.reasoner.tool_runtime import ToolRuntime


def _ai_tool_call(name, args, call_id="call_1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"}])


def _ai_parallel_tool_calls(calls):
    return AIMessage(
        content="",
        tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"} for name, args, call_id in calls],
    )


def _ai_final(text):
    return AIMessage(content=text)


class FakeLLM:
    """A minimal stand-in for the bound DeepSeek chat model: returns a
    scripted sequence of responses, one per .invoke() call."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        self.calls.append(list(messages))
        return self._responses.pop(0)


def _run(responses, question="test question"):
    return _run_with_limit(responses, max_iterations=6, question=question)


def _run_with_limit(responses, max_iterations, question="test question"):
    from app.reasoner.context_builder import context_builder

    fake_llm = FakeLLM(responses)
    reasoner = Reasoner(llm=fake_llm, runtime=ToolRuntime(), max_iterations=max_iterations)
    messages = context_builder.build(question)
    result = reasoner.invoke(messages)
    return result, fake_llm


@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_simple_sql_question(mock_validator, mock_executor):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.return_value = {"success": True, "rows": [{"count": 42}], "row_count": 1}

    responses = [
        _ai_tool_call("sql_verifier", {"sql": "SELECT COUNT(*) FROM products"}),
        _ai_tool_call("sql_executor", {"sql": "SELECT COUNT(*) FROM products"}),
        _ai_final("There are 42 products."),
    ]
    result, _ = _run(responses, "How many products do we have?")

    assert result["answer"] == "There are 42 products."
    assert result["tools_used"] == ["sql_verifier", "sql_executor"]
    mock_validator.invoke.assert_called_once()
    mock_executor.invoke.assert_called_once()


@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_analytical_sql_question(mock_validator, mock_executor):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.return_value = {
        "success": True,
        "rows": [{"category": "Dairy", "total_sales": 15000}, {"category": "Bakery", "total_sales": 9000}],
        "row_count": 2,
    }

    responses = [
        _ai_tool_call("sql_verifier", {"sql": "SELECT category, SUM(total) FROM sales GROUP BY category"}),
        _ai_tool_call("sql_executor", {"sql": "SELECT category, SUM(total) FROM sales GROUP BY category"}),
        _ai_final("Dairy leads with 15,000 in sales, followed by Bakery at 9,000."),
    ]
    result, _ = _run(responses, "Which product category sells the most?")

    assert "Dairy" in result["answer"]
    assert result["tools_used"] == ["sql_verifier", "sql_executor"]


@patch("app.reasoner.tool_runtime.rag_retriever")
def test_rag_question(mock_rag):
    mock_rag.invoke.return_value = {
        "success": True,
        "results": [{"content": "Refunds are accepted within 30 days.", "source": "Chapter_5.md"}],
        "result_count": 1,
    }

    responses = [
        _ai_tool_call("rag", {"query": "what is the refund policy"}),
        _ai_final("Refunds are accepted within 30 days of purchase."),
    ]
    result, _ = _run(responses, "What is our refund policy?")

    assert "30 days" in result["answer"]
    assert result["tools_used"] == ["rag"]
    mock_rag.invoke.assert_called_once()


@patch("app.reasoner.tool_runtime.calculator_tool")
def test_calculator_question(mock_calculator):
    mock_calculator.invoke.return_value = {"success": True, "result": 30}

    responses = [
        _ai_tool_call("calculator", {"expression": "20% of 150"}),
        _ai_final("20% of 150 is 30."),
    ]
    result, _ = _run(responses, "What is 20% of 150?")

    assert "30" in result["answer"]
    assert result["tools_used"] == ["calculator"]


@patch("app.reasoner.tool_runtime.browser_tool")
def test_browser_question(mock_browser):
    mock_browser.invoke.return_value = {
        "success": True,
        "answer": "The current price is approximately $45 per bag.",
        "results": [],
    }

    responses = [
        _ai_tool_call("browser", {"query": "current wholesale price of rice"}),
        _ai_final("Rice is currently around $45 per bag wholesale."),
    ]
    result, _ = _run(responses, "What is the current wholesale price of rice?")

    assert "$45" in result["answer"]
    assert result["tools_used"] == ["browser"]


@patch("app.reasoner.tool_runtime.calculator_tool")
@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_sql_then_calculator(mock_validator, mock_executor, mock_calculator):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.return_value = {"success": True, "rows": [{"total_revenue": 1000}], "row_count": 1}
    mock_calculator.invoke.return_value = {"success": True, "result": 100}

    responses = [
        _ai_tool_call("sql_verifier", {"sql": "SELECT SUM(total) AS total_revenue FROM sales"}),
        _ai_tool_call("sql_executor", {"sql": "SELECT SUM(total) AS total_revenue FROM sales"}),
        _ai_tool_call("calculator", {"expression": "1000 * 0.10"}),
        _ai_final("A 10% commission on 1000 in revenue is 100."),
    ]
    result, _ = _run(responses, "What is 10% commission on our total revenue?")

    assert result["tools_used"] == ["sql_verifier", "sql_executor", "calculator"]
    assert "100" in result["answer"]


@patch("app.reasoner.tool_runtime.gmail_tool")
@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_sql_then_mail(mock_validator, mock_executor, mock_gmail):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.return_value = {"success": True, "rows": [{"total": 42}], "row_count": 1}
    mock_gmail.invoke.return_value = {"success": True, "message": "Email sent successfully."}

    responses = [
        _ai_tool_call("sql_verifier", {"sql": "SELECT COUNT(*) AS total FROM products"}),
        _ai_tool_call("sql_executor", {"sql": "SELECT COUNT(*) AS total FROM products"}),
        _ai_tool_call(
            "mail",
            {"recipient": "owner@example.com", "subject": "Product count", "body": "We currently have 42 products."},
        ),
        _ai_final("I've emailed owner@example.com the product count: 42."),
    ]
    result, _ = _run(responses, "Email the total product count to owner@example.com")

    assert result["tools_used"] == ["sql_verifier", "sql_executor", "mail"]
    mock_gmail.invoke.assert_called_once_with("owner@example.com", "Product count", "We currently have 42 products.")


@patch("app.reasoner.tool_runtime.browser_tool")
@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_sql_plus_browser_parallel(mock_validator, mock_executor, mock_browser):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.return_value = {"success": True, "rows": [{"stock": 120}], "row_count": 1}
    mock_browser.invoke.return_value = {"success": True, "answer": "Market price is $2 per kg.", "results": []}

    responses = [
        _ai_tool_call("sql_verifier", {"sql": "SELECT quantity AS stock FROM inventory WHERE product_id = 1"}),
        _ai_parallel_tool_calls(
            [
                ("sql_executor", {"sql": "SELECT quantity AS stock FROM inventory WHERE product_id = 1"}, "call_sql"),
                ("browser", {"query": "current market price of rice per kg"}, "call_web"),
            ]
        ),
        _ai_final("We have 120 units in stock, and the current market price is about $2 per kg."),
    ]
    result, _ = _run(responses, "How much rice do we have in stock, and what's the current market price?")

    assert result["tools_used"] == ["sql_verifier", "sql_executor", "browser"]
    assert "120" in result["answer"]
    assert "$2" in result["answer"]
    mock_executor.invoke.assert_called_once()
    mock_browser.invoke.assert_called_once()


@patch("app.reasoner.tool_runtime.calculator_tool")
def test_max_iterations_reached_returns_safe_message(mock_calculator):
    mock_calculator.invoke.return_value = {"success": True, "result": 2}

    responses = [
        _ai_tool_call("calculator", {"expression": "1+1"}, "call_1"),
        _ai_tool_call("calculator", {"expression": "1+1"}, "call_2"),
    ]
    result, _ = _run_with_limit(responses, max_iterations=2, question="loop forever")

    assert "could not finish" in result["answer"].lower()
    assert len(result["tools_used"]) == 2
