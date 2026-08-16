"""Tests for the dynamic Pandas code generation analysis pipeline."""

from __future__ import annotations

import unittest
from typing import Any

import pandas as pd

from app.agents.analysis_agent import AnalysisAgent
from app.analysis.executor import analyse, CodeExecutionError


SALES_ROWS = [
    {"order_date": "2026-01-05", "total_amount": 100, "customer_id": 1, "customer_name": "Acme", "product_name": "Laptop", "quantity": 2, "category": "Computers"},
    {"order_date": "2026-01-20", "total_amount": 200, "customer_id": 2, "customer_name": "Bravo", "product_name": "Mouse", "quantity": 8, "category": "Accessories"},
    {"order_date": "2026-02-10", "total_amount": 300, "customer_id": 1, "customer_name": "Acme", "product_name": "Laptop", "quantity": 3, "category": "Computers"},
]


class StubSqlAgent:
    def __init__(self, rows, success=True) -> None:
        self.rows = rows
        self.success = success
        self.calls = 0

    def invoke(self, question: str) -> dict:
        self.calls += 1
        if not self.success:
            return {"status": "error", "tool": "sql", "summary": "Database lookup failed.", "error": "Database lookup failed.", "data": None, "metadata": {}}
        return {"status": "success", "tool": "sql", "data": self.rows, "summary": "unused", "error": None, "metadata": {}}


class ExecutorTests(unittest.TestCase):
    """Direct tests for the code executor with known safe and unsafe inputs."""

    def test_basic_groupby_and_sum(self):
        dfs = {"orders": pd.DataFrame(SALES_ROWS)}
        code = "result = orders.groupby('category')['total_amount'].sum().reset_index().to_dict(orient='records')"
        result = analyse(code, dfs)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_filter_and_count(self):
        dfs = {"orders": pd.DataFrame(SALES_ROWS)}
        code = "result = [{'count': int((orders['total_amount'] > 150).sum())}]"
        result = analyse(code, dfs)
        self.assertEqual(result[0]["count"], 2)

    def test_simple_scalar_result(self):
        dfs = {"orders": pd.DataFrame(SALES_ROWS)}
        code = "result = [{'total': float(orders['total_amount'].sum())}]"
        result = analyse(code, dfs)
        self.assertEqual(result[0]["total"], 600.0)

    def test_returns_dict_for_pivot(self):
        dfs = {"orders": pd.DataFrame(SALES_ROWS)}
        code = """
orders['month'] = pd.to_datetime(orders['order_date']).dt.to_period('M').astype(str)
result = orders.groupby('month')['total_amount'].sum().reset_index().to_dict(orient='records')
"""
        result = analyse(code, dfs)
        self.assertEqual(len(result), 2)

    def test_rejects_code_without_result_variable(self):
        with self.assertRaises(CodeExecutionError):
            analyse("x = 1 + 2", {"orders": pd.DataFrame(SALES_ROWS)})

    def test_rejects_code_with_syntax_error(self):
        with self.assertRaises(CodeExecutionError):
            analyse("result = orders[", {"orders": pd.DataFrame(SALES_ROWS)})

    def test_rejects_dangerous_builtins(self):
        with self.assertRaises(CodeExecutionError):
            analyse("result = __import__('os').listdir('.')", {"orders": pd.DataFrame(SALES_ROWS)})

    def test_handles_nan_values_gracefully(self):
        code = "import math; result = [{'v': float('nan')}]"
        with self.assertRaises(CodeExecutionError):
            analyse(code, {"orders": pd.DataFrame(SALES_ROWS)})


class AnalysisAgentTests(unittest.TestCase):
    """Tests the AnalysisAgent with a stubbed SQL agent and deterministic LLM."""

    def test_returns_error_when_sql_fails(self):
        agent = AnalysisAgent(StubSqlAgent([], success=False))
        result = agent.invoke("Show me revenue")
        self.assertEqual(result["status"], "error")

    def test_returns_error_when_no_dataframes_loaded(self):
        """All DATA_QUERIES return empty — should give a no-data error."""
        sql = StubSqlAgent([], success=True)
        agent = AnalysisAgent(sql)
        result = agent.invoke("Analyze anything")
        self.assertEqual(result["status"], "error")
        self.assertIn("No business data", result["error"])

    def test_tool_contract_keys(self):
        sql = StubSqlAgent([], success=True)
        agent = AnalysisAgent(sql)
        result = agent.invoke("test")
        self.assertIn("status", result)
        self.assertIn("tool", result)
        self.assertIn("data", result)
        self.assertIn("summary", result)
        self.assertIn("error", result)

    def test_tool_contract_is_analysis_tool(self):
        sql = StubSqlAgent([], success=True)
        agent = AnalysisAgent(sql)
        result = agent.invoke("test")
        self.assertEqual(result["tool"], "analysis")


if __name__ == "__main__":
    unittest.main()