"""Small, reusable KPI calculations that work directly on DataFrames."""

import pandas as pd


def total_revenue(dataframe: pd.DataFrame, revenue_column: str = "total_amount") -> float | None:
    if dataframe.empty or revenue_column not in dataframe:
        return None
    return float(pd.to_numeric(dataframe[revenue_column], errors="coerce").fillna(0).sum())


def order_count(dataframe: pd.DataFrame) -> int:
    return int(len(dataframe))


def average_order_value(dataframe: pd.DataFrame, revenue_column: str = "total_amount") -> float | None:
    revenue = total_revenue(dataframe, revenue_column)
    return round(revenue / len(dataframe), 2) if revenue is not None and len(dataframe) else None


def customer_count(dataframe: pd.DataFrame, customer_column: str = "customer_id") -> int | None:
    if dataframe.empty or customer_column not in dataframe:
        return None
    return int(dataframe[customer_column].nunique(dropna=True))


def inventory_value(dataframe: pd.DataFrame) -> float | None:
    if dataframe.empty or not {"quantity", "unit_price"}.issubset(dataframe.columns):
        return None
    quantity = pd.to_numeric(dataframe["quantity"], errors="coerce").fillna(0)
    unit_price = pd.to_numeric(dataframe["unit_price"], errors="coerce").fillna(0)
    return float((quantity * unit_price).sum())


def gross_profit(
    dataframe: pd.DataFrame,
    revenue_column: str = "total_amount",
    cost_column: str = "cost_amount",
) -> float | None:
    """Return profit only when both revenue and cost are present in the SQL result."""
    if dataframe.empty or revenue_column not in dataframe or cost_column not in dataframe:
        return None
    revenue = pd.to_numeric(dataframe[revenue_column], errors="coerce").fillna(0).sum()
    cost = pd.to_numeric(dataframe[cost_column], errors="coerce").fillna(0).sum()
    return float(revenue - cost)


def inventory_turnover(
    dataframe: pd.DataFrame,
    sold_quantity_column: str = "sold_quantity",
    inventory_quantity_column: str = "quantity",
) -> float | None:
    """Calculate turnover when the SQL result provides sold and on-hand quantities."""
    if dataframe.empty or not {sold_quantity_column, inventory_quantity_column}.issubset(dataframe.columns):
        return None
    sold = pd.to_numeric(dataframe[sold_quantity_column], errors="coerce").fillna(0).sum()
    inventory = pd.to_numeric(dataframe[inventory_quantity_column], errors="coerce").fillna(0).sum()
    return round(float(sold / inventory), 2) if inventory else None


def growth_percentage(previous_value: float | int | None, current_value: float | int | None) -> float | None:
    if previous_value in (None, 0) or current_value is None:
        return None
    return round((float(current_value) - float(previous_value)) / float(previous_value) * 100, 2)
