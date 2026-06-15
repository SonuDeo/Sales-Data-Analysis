"""Headline KPIs for the sales dataset."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class SalesKPIs:
    """Aggregate business metrics for the whole dataset."""

    total_orders: int
    total_records: int
    total_customers: int
    total_sales: float
    total_profit: float
    total_quantity: int
    avg_order_value: float
    overall_profit_margin: float
    avg_discount: float
    avg_days_to_ship: float
    loss_making_order_share: float
    first_order_date: str
    last_order_date: str

    def as_dict(self) -> dict:
        return asdict(self)


def compute_kpis(df: pd.DataFrame) -> SalesKPIs:
    """Compute headline KPIs from a cleaned dataframe."""
    total_sales = float(df["sales"].sum())
    total_profit = float(df["profit"].sum())
    unique_orders = df["order_id"].nunique()

    # Average order value is computed per real order, not per line item.
    order_totals = df.groupby("order_id")["sales"].sum()
    avg_order_value = float(order_totals.mean()) if not order_totals.empty else 0.0

    loss_share = float((df["profit"] < 0).mean()) if len(df) else 0.0

    return SalesKPIs(
        total_orders=int(unique_orders),
        total_records=int(len(df)),
        total_customers=int(df["customer_name"].nunique()),
        total_sales=round(total_sales, 2),
        total_profit=round(total_profit, 2),
        total_quantity=int(df["quantity"].sum()),
        avg_order_value=round(avg_order_value, 2),
        overall_profit_margin=round(total_profit / total_sales, 4)
        if total_sales
        else 0.0,
        avg_discount=round(float(df["discount"].mean()), 4),
        avg_days_to_ship=round(float(df["days_to_ship"].mean()), 2),
        loss_making_order_share=round(loss_share, 4),
        first_order_date=str(df["order_date"].min().date()),
        last_order_date=str(df["order_date"].max().date()),
    )
