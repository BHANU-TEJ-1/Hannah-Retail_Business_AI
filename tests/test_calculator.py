from app.tools.calculator_tool import calculator_tool


def test_arithmetic():
    result = calculator_tool.invoke("25 + 18")
    assert result["success"] is True
    assert result["result"] == 43


def test_percentage():
    result = calculator_tool.invoke("20% of 150")
    assert result["success"] is True
    assert result["result"] == 30


def test_multiple_operations():
    result = calculator_tool.invoke("(100 + 50) * 2 - 10")
    assert result["success"] is True
    assert result["result"] == 290


def test_invalid_expression():
    result = calculator_tool.invoke("banana + 5")
    assert result["success"] is False
    assert "error" in result


def test_empty_expression():
    result = calculator_tool.invoke("")
    assert result["success"] is False
