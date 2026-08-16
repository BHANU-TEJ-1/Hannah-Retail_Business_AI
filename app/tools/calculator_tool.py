import ast
import operator
import re


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_PERCENT_OF = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")


class Calculator:
    """Deterministic arithmetic evaluation. No LLM involvement - the Reasoner
    decides what to calculate, this tool only computes the result."""

    name = "calculator"
    description = "Evaluates a deterministic arithmetic expression, including percentages."

    def invoke(self, expression: str) -> dict:
        if expression is None or not expression.strip():
            return {"success": False, "error": "Expression is empty."}

        try:
            normalized = self._normalize(expression)
            tree = ast.parse(normalized, mode="eval")
            result = self._eval(tree.body)
            return {"success": True, "expression": expression, "result": result}

        except Exception:
            return {"success": False, "error": "Invalid mathematical expression."}

    def _normalize(self, expression: str) -> str:
        text = expression.strip()
        # "20% of 150" -> "(20/100)*150"
        text = _PERCENT_OF.sub(r"(\1/100)*\2", text)
        # remaining standalone "20%" -> "(20/100)"
        text = _PERCENT.sub(r"(\1/100)", text)
        return text

    def _eval(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            left = self._eval(node.left)
            right = self._eval(node.right)
            return _OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](self._eval(node.operand))

        raise ValueError("Unsupported expression")


calculator_tool = Calculator()
