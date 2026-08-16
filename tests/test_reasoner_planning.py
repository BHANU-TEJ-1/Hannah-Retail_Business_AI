"""Tests that the Reasoner plans and follows through on multi-step tasks
instead of stopping early, and that it skips tools when it doesn't need
them. Uses the same scripted-FakeLLM approach as test_reasoner.py - no real
network call to OpenRouter/DeepSeek, and every underlying tool is mocked at
its source.
"""

from unittest.mock import patch

from app.reasoner.context_builder import context_builder
from app.reasoner.reasoner import Reasoner
from app.reasoner.tool_runtime import ToolRuntime
from tests.test_reasoner import FakeLLM, _ai_final, _ai_tool_call


def _run(responses, question="test question", max_iterations=12):
    fake_llm = FakeLLM(responses)
    reasoner = Reasoner(llm=fake_llm, runtime=ToolRuntime(), max_iterations=max_iterations)
    messages = context_builder.build(question)
    result = reasoner.invoke(messages)
    return result, fake_llm


# ---------------------------------------------------------------------------
# 1. General reasoning - no tool should be called at all
# ---------------------------------------------------------------------------

def test_profit_increase_question_needs_no_tool():
    responses = [
        _ai_final(
            "To increase profit by 10%, raise the selling price by 10% of "
            "the current price (assuming cost stays the same)."
        )
    ]
    result, fake_llm = _run(
        responses,
        "If a product should make a profit increase of 10%, how much should I increase its selling price?",
    )

    assert result["tools_used"] == []
    assert len(fake_llm.calls) == 1


def test_general_aptitude_question_needs_no_tool():
    responses = [_ai_final("The train takes 2 hours to cover 120 km at 60 km/h.")]
    result, _ = _run(responses, "A train travels 120 km at 60 km/h. How long does the trip take?")

    assert result["tools_used"] == []


# ---------------------------------------------------------------------------
# 2. Multi-step planning - mail should not stop after drafting
# ---------------------------------------------------------------------------

@patch("app.reasoner.tool_runtime.gmail_tool")
@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_mail_by_customer_name_looks_up_email_then_sends(mock_validator, mock_executor, mock_gmail):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.return_value = {
        "success": True,
        "rows": [{"name": "Ganasan Developers", "email": "contact@ganasandevelopers.com"}],
        "row_count": 1,
    }
    mock_gmail.invoke.return_value = {"success": True, "message": "Email sent successfully."}

    responses = [
        _ai_tool_call("sql_verifier", {"sql": "SELECT name, email FROM customers WHERE name = 'Ganasan Developers'"}),
        _ai_tool_call("sql_executor", {"sql": "SELECT name, email FROM customers WHERE name = 'Ganasan Developers'"}),
        _ai_tool_call(
            "mail",
            {
                "recipient": "contact@ganasandevelopers.com",
                "subject": "Thank You",
                "body": "Dear Ganasan Developers, thank you for your continued business.",
            },
        ),
        _ai_final("I've sent a thank-you email to Ganasan Developers at contact@ganasandevelopers.com."),
    ]
    result, _ = _run(responses, "Send a thank you mail to customer Ganasan Developers.")

    # Must not stop after the SQL lookup, and must not stop after drafting -
    # mail has to actually be called.
    assert result["tools_used"] == ["sql_verifier", "sql_executor", "mail"]
    mock_gmail.invoke.assert_called_once_with(
        "contact@ganasandevelopers.com", "Thank You", "Dear Ganasan Developers, thank you for your continued business."
    )
    assert "sent" in result["answer"].lower()


# ---------------------------------------------------------------------------
# 3. Database analysis - keeps querying until it has enough data, never
#    refuses when the data exists.
# ---------------------------------------------------------------------------

@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_analysis_issues_a_second_query_when_first_is_insufficient(mock_validator, mock_executor):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.side_effect = [
        # First query: too coarse, only a single total - not enough to analyze a trend.
        {"success": True, "rows": [{"total_sales": 5000}], "row_count": 1},
        # Second, more granular query: daily breakdown.
        {
            "success": True,
            "rows": [
                {"day": "2026-07-01", "units_sold": 10},
                {"day": "2026-07-02", "units_sold": 25},
                {"day": "2026-07-03", "units_sold": 15},
            ],
            "row_count": 3,
        },
    ]

    responses = [
        _ai_tool_call("sql_verifier", {"sql": "SELECT SUM(quantity) AS total_sales FROM sales WHERE product_id = 1"}),
        _ai_tool_call("sql_executor", {"sql": "SELECT SUM(quantity) AS total_sales FROM sales WHERE product_id = 1"}),
        _ai_tool_call(
            "sql_verifier",
            {"sql": "SELECT sale_date AS day, SUM(quantity) AS units_sold FROM sales WHERE product_id = 1 GROUP BY sale_date"},
        ),
        _ai_tool_call(
            "sql_executor",
            {"sql": "SELECT sale_date AS day, SUM(quantity) AS units_sold FROM sales WHERE product_id = 1 GROUP BY sale_date"},
        ),
        _ai_final(
            "Product 1 sold 50 units last month across 3 active days, peaking on July 2nd with 25 units."
        ),
    ]
    result, _ = _run(responses, "Analyze sales of product id 1 for last month.")

    assert result["tools_used"] == ["sql_verifier", "sql_executor", "sql_verifier", "sql_executor"]
    assert mock_executor.invoke.call_count == 2
    assert "cannot perform analysis" not in result["answer"].lower()
    assert "peaking" in result["answer"].lower() or "50 units" in result["answer"]


# ---------------------------------------------------------------------------
# 4. Tool chaining - compare products via two SQL lookups + reasoning
# ---------------------------------------------------------------------------

@patch("app.reasoner.tool_runtime._sql_executor")
@patch("app.reasoner.tool_runtime.sql_validator")
def test_compare_products_queries_both_then_compares(mock_validator, mock_executor):
    mock_validator.invoke.return_value = {"success": True, "message": "SQL is valid."}
    mock_executor.invoke.return_value = {
        "success": True,
        "rows": [
            {"product_id": 1, "total_sales": 5000},
            {"product_id": 2, "total_sales": 3200},
        ],
        "row_count": 2,
    }

    responses = [
        _ai_tool_call(
            "sql_verifier",
            {"sql": "SELECT product_id, SUM(total) AS total_sales FROM sales WHERE product_id IN (1, 2) GROUP BY product_id"},
        ),
        _ai_tool_call(
            "sql_executor",
            {"sql": "SELECT product_id, SUM(total) AS total_sales FROM sales WHERE product_id IN (1, 2) GROUP BY product_id"},
        ),
        _ai_final("Product 1 outsold product 2, with 5,000 in sales versus 3,200."),
    ]
    result, _ = _run(responses, "Compare the sales of product 1 and product 2.")

    assert result["tools_used"] == ["sql_verifier", "sql_executor"]
    assert "5,000" in result["answer"] or "5000" in result["answer"]


# ---------------------------------------------------------------------------
# 5. Tool minimization - simple math and general knowledge skip tools
# ---------------------------------------------------------------------------

def test_simple_math_skips_calculator_tool():
    responses = [_ai_final("15% of 200 is 30.")]
    result, _ = _run(responses, "What is 15% of 200?")

    assert result["tools_used"] == []


def test_general_knowledge_skips_all_tools():
    responses = [_ai_final("A SKU is a Stock Keeping Unit, a unique code identifying a specific product.")]
    result, _ = _run(responses, "What does SKU stand for?")

    assert result["tools_used"] == []
