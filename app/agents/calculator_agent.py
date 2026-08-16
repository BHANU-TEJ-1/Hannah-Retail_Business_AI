from app.agents.contracts import success, error


class CalculatorAgent:
    def __init__(self, tool=None) -> None:
        from app.tools.calculator_tool import calculator
        self._tool = tool or calculator

    def invoke(self, expression: str) -> dict:
        result = self._tool.invoke({"expression": expression})
        if result.startswith("Calculation Error:"):
            return error("calculator", result).to_dict()
        return success(
            "calculator",
            data={"expression": expression, "result": result},
            summary=result,
        ).to_dict()


calculator_agent = CalculatorAgent()
