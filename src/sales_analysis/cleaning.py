"""Data cleaning and feature engineering."""

from __future__ import annotations

import pandas as pd


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw dataset and add analysis-friendly derived columns.

    The function is pure: it returns a new dataframe and never mutates the
    input. Steps performed:

    * Drop exact duplicate rows.
    * Coerce ``order_date`` / ``ship_date`` to datetime.
    * Add ``month_year`` (period string), ``order_month`` and ``order_year``.
    * Add ``days_to_ship`` (ship_date - order_date in days).
    * Add ``profit_margin`` (profit / sales) guarded against divide-by-zero.
    * Add ``is_profitable`` boolean flag.
    """
    out = df.copy()

    # Remove duplicates that would skew aggregate metrics.
    out = out.drop_duplicates().reset_index(drop=True)

    # Ensure date columns are real datetimes.
    for col in ("order_date", "ship_date"):
        out[col] = pd.to_datetime(out[col], errors="coerce")

    # Time-based features for trend analysis.
    out["month_year"] = out["order_date"].dt.to_period("M").astype(str)
    out["order_year"] = out["order_date"].dt.year
    out["order_month"] = out["order_date"].dt.month

    # Fulfilment speed.
    out["days_to_ship"] = (out["ship_date"] - out["order_date"]).dt.days

    # Profitability features (avoid division by zero).
    out["profit_margin"] = (
        out["profit"].div(out["sales"].where(out["sales"] != 0))
    ).fillna(0.0)
    out["is_profitable"] = out["profit"] > 0

    return out
