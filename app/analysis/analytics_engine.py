"""Focused Pandas calculations for sales, products, customers, and inventory."""

import pandas as pd

from app.analysis.kpis import (
    average_order_value,
    customer_count,
    gross_profit,
    growth_percentage,
    inventory_turnover,
    inventory_value,
    order_count,
    total_revenue,
)
from app.analysis.trends import sales_trend


def revenue_by_category(dataframe: pd.DataFrame) -> list[dict]:
    return _group_total(dataframe, "category", _revenue_column(dataframe))


def revenue_by_customer(dataframe: pd.DataFrame) -> list[dict]:
    column = "customer_name" if "customer_name" in dataframe else "customer_id"
    return _group_total(dataframe, column, _revenue_column(dataframe))


def revenue_by_supplier(dataframe: pd.DataFrame) -> list[dict]:
    column = "supplier_name" if "supplier_name" in dataframe else "supplier_id"
    return _group_total(dataframe, column, _revenue_column(dataframe))


def top_selling_products(dataframe: pd.DataFrame, limit: int = 5, ascending: bool = False) -> list[dict]:
    product_column = "product_name" if "product_name" in dataframe else "name"
    if dataframe.empty or product_column not in dataframe or "quantity" not in dataframe:
        return []
    working = dataframe[[product_column, "quantity"]].copy()
    working["quantity"] = pd.to_numeric(working["quantity"], errors="coerce").fillna(0)
    grouped = working.groupby(product_column, dropna=True)["quantity"].sum().sort_values(ascending=ascending).head(limit)
    return [{"product": str(name), "quantity": float(quantity)} for name, quantity in grouped.items()]


def top_customers(dataframe: pd.DataFrame, limit: int = 5) -> list[dict]:
    column = "customer_name" if "customer_name" in dataframe else "customer_id"
    return _group_total(dataframe, column, _revenue_column(dataframe), limit=limit)


def repeat_customers(dataframe: pd.DataFrame) -> list[dict]:
    column = "customer_name" if "customer_name" in dataframe else "customer_id"
    if dataframe.empty or column not in dataframe:
        return []
    counts = dataframe.groupby(column, dropna=True).size()
    return [{"name": str(name), "order_count": int(count)} for name, count in counts[counts > 1].items()]


def customer_contribution(dataframe: pd.DataFrame) -> list[dict]:
    customers = revenue_by_customer(dataframe)
    total = sum(row["revenue"] for row in customers)
    if not total:
        return customers
    return [
        {**row, "contribution_percentage": round(row["revenue"] / total * 100, 2)}
        for row in customers
    ]


def low_stock(dataframe: pd.DataFrame) -> list[dict]:
    if dataframe.empty or not {"quantity", "reorder_level"}.issubset(dataframe.columns):
        return []
    working = dataframe.copy()
    working["quantity"] = pd.to_numeric(working["quantity"], errors="coerce").fillna(0)
    working["reorder_level"] = pd.to_numeric(working["reorder_level"], errors="coerce").fillna(0)
    return working[working["quantity"] <= working["reorder_level"]].to_dict(orient="records")


def business_kpis(dataframe: pd.DataFrame) -> dict:
    revenue_column = _revenue_column(dataframe)
    revenue = total_revenue(dataframe, revenue_column) if revenue_column else None
    return {
        "total_revenue": revenue,
        "order_count": order_count(dataframe),
        "average_order_value": average_order_value(dataframe, revenue_column) if revenue_column else None,
        "customer_count": customer_count(dataframe),
        "inventory_value": inventory_value(dataframe),
        "gross_profit": gross_profit(dataframe, revenue_column) if revenue_column else None,
        "inventory_turnover": inventory_turnover(dataframe),
    }


def period_growth(dataframe: pd.DataFrame, period: str = "monthly") -> float | None:
    trend = sales_trend(dataframe, period)
    if len(trend) < 2:
        return None
    return growth_percentage(trend[-2]["revenue"], trend[-1]["revenue"])


def _group_total(dataframe: pd.DataFrame, group_column: str, revenue_column: str | None, limit: int | None = None) -> list[dict]:
    if dataframe.empty or not revenue_column or group_column not in dataframe:
        return []
    working = dataframe[[group_column, revenue_column]].copy()
    working[revenue_column] = pd.to_numeric(working[revenue_column], errors="coerce").fillna(0)
    grouped = working.groupby(group_column, dropna=True)[revenue_column].sum().sort_values(ascending=False)
    if limit:
        grouped = grouped.head(limit)
    return [{"name": str(name), "revenue": float(value)} for name, value in grouped.items()]


def _revenue_column(dataframe: pd.DataFrame) -> str | None:
    return next((column for column in ("total_amount", "subtotal", "amount", "revenue") if column in dataframe), None)
