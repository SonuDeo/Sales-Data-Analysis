"""Plotting helpers that persist figures to disk.

All functions use a non-interactive Matplotlib backend so they run headless in
CI or containers. Each function returns the path of the saved figure.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend; must be set before pyplot import

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(style="whitegrid", palette="deep")


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_monthly_sales(monthly: pd.DataFrame, out_dir: Path) -> Path:
    """Line chart of monthly sales and profit over time."""
    fig, ax = plt.subplots(figsize=(13, 6))
    x = pd.PeriodIndex(monthly["month_year"], freq="M").to_timestamp()
    ax.plot(x, monthly["sales"], label="Sales", color="#2c7fb8", linewidth=2)
    ax.plot(x, monthly["profit"], label="Profit", color="#31a354", linewidth=2)
    ax.set_title("Monthly Sales & Profit Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.legend()
    return _save(fig, out_dir / "monthly_sales_trend.png")


def plot_top_products(top: pd.DataFrame, out_dir: Path, by: str = "sales") -> Path:
    """Horizontal bar chart of the top products."""
    fig, ax = plt.subplots(figsize=(11, 7))
    data = top.sort_values(by)
    sns.barplot(data=data, y="product_name", x=by, ax=ax, color="#2c7fb8")
    ax.set_title(f"Top {len(top)} Products by {by.title()}")
    ax.set_xlabel(by.title())
    ax.set_ylabel("")
    return _save(fig, out_dir / f"top_products_by_{by}.png")


def plot_segment_distribution(rfm: pd.DataFrame, out_dir: Path) -> Path:
    """Bar chart of customer counts per RFM segment."""
    fig, ax = plt.subplots(figsize=(11, 6))
    counts = rfm["segment"].value_counts()
    sns.barplot(x=counts.values, y=counts.index, ax=ax, color="#756bb1")
    ax.set_title("Customer Distribution by RFM Segment")
    ax.set_xlabel("Number of Customers")
    ax.set_ylabel("")
    return _save(fig, out_dir / "rfm_segments.png")


def plot_category_profit(df: pd.DataFrame, out_dir: Path) -> Path:
    """Bar chart of profit by category / sub-category."""
    fig, ax = plt.subplots(figsize=(12, 7))
    data = (
        df.groupby(["category", "sub_category"])["profit"]
        .sum()
        .reset_index()
        .sort_values("profit")
    )
    sns.barplot(data=data, y="sub_category", x="profit", hue="category", ax=ax)
    ax.set_title("Profit by Sub-Category")
    ax.set_xlabel("Profit")
    ax.set_ylabel("")
    ax.legend(title="Category")
    return _save(fig, out_dir / "profit_by_subcategory.png")
