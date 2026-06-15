"""Plotting helpers that persist figures to disk.

All functions use a non-interactive Matplotlib backend so they run headless in
CI or containers. Each function returns the path of the saved figure.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend; must be set before pyplot import

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

# ---------------------------------------------------------------------------
# Global theme - a clean, modern look shared by every chart.
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#d0d0d0",
        "axes.titleweight": "bold",
        "axes.titlesize": 16,
        "axes.titlepad": 14,
        "axes.labelcolor": "#333333",
        "axes.labelsize": 12,
        "font.family": "DejaVu Sans",
        "axes.grid": True,
        "grid.color": "#ececec",
        "savefig.facecolor": "white",
    }
)

# Brand palette used across charts.
PRIMARY = "#2563eb"  # blue
ACCENT = "#16a34a"  # green
PURPLE = "#7c3aed"
PALETTE = ["#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#7c3aed", "#0891b2"]


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path


def _currency_formatter() -> mticker.FuncFormatter:
    """Format large axis numbers as $1.2K / $3.4M for readability."""

    def _fmt(x: float, _pos: int) -> str:
        for unit, div in (("M", 1_000_000), ("K", 1_000)):
            if abs(x) >= div:
                return f"${x / div:.1f}{unit}"
        return f"${x:.0f}"

    return mticker.FuncFormatter(_fmt)


def plot_monthly_sales(monthly: pd.DataFrame, out_dir: Path) -> Path:
    """Line chart of monthly sales and profit over time."""
    fig, ax = plt.subplots(figsize=(13, 6))
    x = pd.PeriodIndex(monthly["month_year"], freq="M").to_timestamp()

    ax.plot(x, monthly["sales"], label="Sales", color=PRIMARY, linewidth=2.5)
    ax.fill_between(x, monthly["sales"], color=PRIMARY, alpha=0.08)
    ax.plot(x, monthly["profit"], label="Profit", color=ACCENT, linewidth=2.5)
    ax.fill_between(x, monthly["profit"], color=ACCENT, alpha=0.08)

    ax.set_title("Monthly Sales & Profit Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (USD)")
    ax.yaxis.set_major_formatter(_currency_formatter())
    ax.legend(frameon=False, loc="upper left")
    ax.margins(x=0.01)
    sns.despine(ax=ax)
    return _save(fig, out_dir / "monthly_sales_trend.png")


def plot_top_products(top: pd.DataFrame, out_dir: Path, by: str = "sales") -> Path:
    """Horizontal bar chart of the top products with value labels."""
    fig, ax = plt.subplots(figsize=(12, 7))
    data = top.sort_values(by)
    bars = ax.barh(data["product_name"], data[by], color=PRIMARY)

    is_currency = by in {"sales", "profit"}
    span = data[by].max() or 1
    for bar in bars:
        width = bar.get_width()
        label = f"${width:,.0f}" if is_currency else f"{width:,.0f}"
        ax.text(
            width + span * 0.01,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center",
            fontsize=10,
            color="#333333",
        )

    ax.set_title(f"Top {len(top)} Products by {by.title()}")
    ax.set_xlabel(by.title())
    ax.set_ylabel("")
    if is_currency:
        ax.xaxis.set_major_formatter(_currency_formatter())
    ax.margins(x=0.12)
    sns.despine(ax=ax, left=True)
    return _save(fig, out_dir / f"top_products_by_{by}.png")


def plot_segment_distribution(rfm: pd.DataFrame, out_dir: Path) -> Path:
    """Bar chart of customer counts per RFM segment with value labels."""
    fig, ax = plt.subplots(figsize=(12, 6))
    counts = rfm["segment"].value_counts()
    colors = (PALETTE * (len(counts) // len(PALETTE) + 1))[: len(counts)]
    bars = ax.barh(counts.index[::-1], counts.values[::-1], color=colors[::-1])

    span = counts.max() or 1
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + span * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}",
            va="center",
            fontsize=11,
            color="#333333",
        )

    ax.set_title("Customer Distribution by RFM Segment")
    ax.set_xlabel("Number of Customers")
    ax.set_ylabel("")
    ax.margins(x=0.1)
    sns.despine(ax=ax, left=True)
    return _save(fig, out_dir / "rfm_segments.png")


def plot_category_profit(df: pd.DataFrame, out_dir: Path) -> Path:
    """Diverging bar chart of profit by sub-category (loss vs profit highlighted)."""
    fig, ax = plt.subplots(figsize=(12, 8))
    data = (
        df.groupby(["category", "sub_category"])["profit"]
        .sum()
        .reset_index()
        .sort_values("profit")
    )
    colors = [ACCENT if v >= 0 else "#ef4444" for v in data["profit"]]
    ax.barh(data["sub_category"], data["profit"], color=colors)

    ax.axvline(0, color="#999999", linewidth=1)
    ax.set_title("Profit by Sub-Category (loss-makers in red)")
    ax.set_xlabel("Profit (USD)")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(_currency_formatter())
    sns.despine(ax=ax, left=True)
    return _save(fig, out_dir / "profit_by_subcategory.png")
