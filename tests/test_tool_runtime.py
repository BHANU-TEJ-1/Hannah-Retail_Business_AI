import json
from unittest.mock import patch

from app.reasoner.tool_runtime import ToolRuntime


def _call(name, args, call_id="call_1"):
    return {"name": name, "args": args, "id": call_id}


@patch("app.reasoner.tool_runtime.calculator_tool")
def test_single_tool_call_dispatches_to_the_right_tool(mock_calculator):
    mock_calculator.invoke.return_value = {"success": True, "result": 43}

    runtime = ToolRuntime()
    messages = runtime.run([_call("calculator", {"expression": "25 + 18"})])

    assert len(messages) == 1
    assert messages[0].tool_call_id == "call_1"
    assert json.loads(messages[0].content) == {"success": True, "result": 43}
    mock_calculator.invoke.assert_called_once_with("25 + 18")


@patch("app.reasoner.tool_runtime.browser_tool")
@patch("app.reasoner.tool_runtime._sql_executor")
def test_parallel_independent_tool_calls_preserve_order(mock_sql_executor, mock_browser):
    mock_sql_executor.invoke.return_value = {"success": True, "rows": [{"total": 10}]}
    mock_browser.invoke.return_value = {"success": True, "results": []}

    runtime = ToolRuntime()
    calls = [
        _call("sql_executor", {"sql": "SELECT COUNT(*) AS total FROM products"}, "call_a"),
        _call("browser", {"query": "current market price of rice"}, "call_b"),
    ]
    messages = runtime.run(calls)

    assert [message.tool_call_id for message in messages] == ["call_a", "call_b"]
    assert json.loads(messages[0].content)["rows"] == [{"total": 10}]
    assert json.loads(messages[1].content)["success"] is True


def test_unknown_tool_returns_structured_error():
    runtime = ToolRuntime()
    messages = runtime.run([_call("not_a_real_tool", {})])

    result = json.loads(messages[0].content)
    assert result["success"] is False
    assert "Unknown tool" in result["error"]


@patch("app.reasoner.tool_runtime.calculator_tool")
def test_tool_exception_is_caught_and_structured(mock_calculator):
    mock_calculator.invoke.side_effect = Exception("boom")

    runtime = ToolRuntime()
    messages = runtime.run([_call("calculator", {"expression": "1+1"})])

    result = json.loads(messages[0].content)
    assert result["success"] is False
    assert "error" in result
