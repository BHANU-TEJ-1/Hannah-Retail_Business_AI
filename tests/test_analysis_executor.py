"""Unit tests for the restricted Python executor used by the Analysis Agent."""

from __future__ import annotations

import unittest

import pandas as pd

from app.analysis.executor import analyse, CodeExecutionError


SAMPLE_ORDERS = pd.DataFrame([
    {"order_date": "2026-01-05", "total_amount": 100, "customer_id": 1, "product": "A", "qty": 2},
    {"order_date": "2026-01-20", "total_amount": 200, "customer_id": 2, "product": "B", "qty": 8},
    {"order_date": "2026-02-10", "total_amount": 300, "customer_id": 1, "product": "A", "qty": 3},
])

SAMPLE_PRODUCTS = pd.DataFrame([
    {"product": "A", "category": "Electronics", "price": 50},
    {"product": "B", "category": "Accessories", "price": 25},
])


class ExecutorSafetyTests(unittest.TestCase):
    """Verify the executor blocks dangerous operations."""

    def test_rejects_file_read(self):
        with self.assertRaises(CodeExecutionError):
            analyse("result = open('/etc/passwd').read()", {"df": SAMPLE_ORDERS})

    def test_rejects_import_inside_code(self):
        with self.assertRaises(CodeExecutionError):
            analyse("import os; result = os.listdir('.')", {"df": SAMPLE_ORDERS})

    def test_rejects_subprocess(self):
        with self.assertRaises(CodeExecutionError):
            analyse("import subprocess; result = subprocess.run(['ls'])", {"df": SAMPLE_ORDERS})

    def test_rejects_eval(self):
        with self.assertRaises(CodeExecutionError):
            analyse("result = eval('1+1')", {"df": SAMPLE_ORDERS})

    def test_rejects_exec_nested(self):
        with self.assertRaises(CodeExecutionError):
            analyse("exec('result = 1')", {"df": SAMPLE_ORDERS})

    def test_rejects_missing_result(self):
        with self.assertRaises(CodeExecutionError):
            analyse("x = 42", {"df": SAMPLE_ORDERS})

    def test_rejects_syntax_error(self):
        with self.assertRaises(CodeExecutionError):
            analyse("result = df[", {"df": SAMPLE_ORDERS})


class ExecutorFunctionalTests(unittest.TestCase):
    """Verify the executor produces correct results for valid Pandas code."""

    def test_total_revenue(self):
        code = "result = [{'total': float(df['total_amount'].sum())}]"
        result = analyse(code, {"df": SAMPLE_ORDERS})
        self.assertAlmostEqual(result[0]["total"], 600.0)

    def test_groupby_sum(self):
        code = """
result = df.groupby('product')['qty'].sum().reset_index().to_dict(orient='records')
"""
        result = analyse(code, {"df": SAMPLE_ORDERS})
        self.assertEqual(len(result), 2)

    def test_filtered_result(self):
        code = "result = df[df['total_amount'] > 150].to_dict(orient='records')"
        result = analyse(code, {"df": SAMPLE_ORDERS})
        self.assertEqual(len(result), 2)

    def test_join_two_dataframes(self):
        code = """
merged = df.merge(products, on='product')
result = merged.groupby('category')['total_amount'].sum().reset_index().to_dict(orient='records')
"""
        result = analyse(code, {"df": SAMPLE_ORDERS, "products": SAMPLE_PRODUCTS})
        self.assertEqual(len(result), 2)

    def test_scalar_result_converted_via_item(self):
        code = "result = [{'avg': float(df['total_amount'].mean())}]"
        result = analyse(code, {"df": SAMPLE_ORDERS})
        self.assertAlmostEqual(result[0]["avg"], 200.0)

    def test_empty_dataframe(self):
        empty = pd.DataFrame()
        code = "result = [{'count': len(df)}]"
        result = analyse(code, {"df": empty})
        self.assertEqual(result[0]["count"], 0)


if __name__ == "__main__":
    unittest.main()