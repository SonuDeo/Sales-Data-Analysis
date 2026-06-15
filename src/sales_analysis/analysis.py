"""Advanced analytics: trends, rankings, RFM customer segmentation."""

from __future__ import annotations

import pandas as pd


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly aggregated sales, profit and order counts.

    The result is sorted chronologically and indexed by ``month_year``.
    """
    grouped = (
        df.groupby("month_year")
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
            quantity=("quantity", "sum"),
        )
        .reset_index()
    )
    grouped["month_year"] = pd.PeriodIndex(grouped["month_year"], freq="M")
    grouped = grouped.sort_values("month_year").reset_index(drop=True)
    # Month-over-month growth in sales.
    grouped["sales_mom_growth"] = grouped["sales"].pct_change().round(4)
    grouped["month_year"] = grouped["month_year"].astype(str)
    return grouped


def top_products(df: pd.DataFrame, by: str = "sales", n: int = 10) -> pd.DataFrame:
    """Return the top ``n`` products ranked by ``by`` (sales/profit/quantity)."""
    if by not in {"sales", "profit", "quantity"}:
        raise ValueError("`by` must be one of 'sales', 'profit', 'quantity'")
    ranked = (
        df.groupby("product_name")
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            quantity=("quantity", "sum"),
        )
        .sort_values(by, ascending=False)
        .head(n)
        .reset_index()
    )
    return ranked


def top_customers(df: pd.DataFrame, by: str = "sales", n: int = 10) -> pd.DataFrame:
    """Return the top ``n`` customers ranked by ``by`` (sales/profit)."""
    if by not in {"sales", "profit"}:
        raise ValueError("`by` must be one of 'sales', 'profit'")
    ranked = (
        df.groupby("customer_name")
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values(by, ascending=False)
        .head(n)
        .reset_index()
    )
    return ranked


def days_to_ship_distribution(df: pd.DataFrame) -> pd.Series:
    """Return the distribution (counts) of days-to-ship values."""
    return df["days_to_ship"].value_counts().sort_index()


def rfm_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """Compute an RFM (Recency, Frequency, Monetary) customer segmentation.

    Recency is measured in days relative to the most recent order in the
    dataset. Each dimension is scored 1-4 using quartiles, then combined into a
    coarse, human-readable segment label.

    Returns one row per customer with the raw RFM values, the component scores,
    the combined ``RFM_score`` string and a ``segment`` label.
    """
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_name").agg(
        recency=("order_date", lambda x: (snapshot_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("sales", "sum"),
    )

    # Score each dimension into quartiles (1 = worst, 4 = best).
    # Recency is reversed: a smaller recency (more recent) is better.
    r_labels = range(4, 0, -1)
    fm_labels = range(1, 5)

    rfm["R"] = _safe_qcut(rfm["recency"], r_labels)
    rfm["F"] = _safe_qcut(rfm["frequency"].rank(method="first"), fm_labels)
    rfm["M"] = _safe_qcut(rfm["monetary"], fm_labels)

    rfm["RFM_score"] = (
        rfm["R"].astype(int).astype(str)
        + rfm["F"].astype(int).astype(str)
        + rfm["M"].astype(int).astype(str)
    )
    rfm["segment"] = rfm.apply(_segment_label, axis=1)

    return rfm.reset_index()


def _safe_qcut(series: pd.Series, labels) -> pd.Series:
    """qcut wrapper that degrades gracefully when there are too few unique values."""
    labels = list(labels)
    try:
        return pd.qcut(series, q=len(labels), labels=labels, duplicates="drop").astype(int)
    except ValueError:
        # Not enough distinct values to form the requested number of bins.
        ranked = series.rank(method="first")
        binned = pd.cut(ranked, bins=len(labels), labels=labels)
        return binned.astype(int)


def _segment_label(row: pd.Series) -> str:
    """Map RFM component scores onto a small set of marketing segments."""
    r, f, m = int(row["R"]), int(row["F"]), int(row["M"])
    if r >= 3 and f >= 3 and m >= 3:
        return "Champions"
    if f >= 3 and m >= 3:
        return "Loyal Customers"
    if r >= 3 and m >= 3:
        return "Big Spenders"
    if r >= 3 and f <= 2:
        return "New / Promising"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r == 1 and f == 1:
        return "Lost"
    return "Needs Attention"
