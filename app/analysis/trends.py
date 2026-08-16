"""Date-based sales trend calculations using Pandas grouping operations."""

import pandas as pd


def sales_trend(
    dataframe: pd.DataFrame,
    period: str,
    date_column: str = "order_date",
    revenue_column: str = "total_amount",
) -> list[dict]:
    """Return deterministic daily, weekly, monthly, quarterly, or yearly revenue totals."""
    if dataframe.empty or date_column not in dataframe or revenue_column not in dataframe:
        return []
    frequency = {"daily": "D", "weekly": "W", "monthly": "MS", "quarterly": "QS", "yearly": "YS"}.get(period)
    if frequency is None:
        return []
    working = dataframe[[date_column, revenue_column]].copy()
    working[date_column] = pd.to_datetime(working[date_column], errors="coerce")
    working[revenue_column] = pd.to_numeric(working[revenue_column], errors="coerce").fillna(0)
    working = working.dropna(subset=[date_column])
    if working.empty:
        return []
    grouped = working.set_index(date_column)[revenue_column].resample(frequency).sum().reset_index()
    # Omit periods that have no source records; this keeps the trend focused on
    # observed business activity instead of adding artificial zero-value dates.
    grouped = grouped[grouped[revenue_column] != 0]
    return [
        {"period": row[date_column].strftime("%Y-%m-%d"), "revenue": float(row[revenue_column])}
        for _, row in grouped.iterrows()
    ]
