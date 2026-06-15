"""End-to-end orchestration of the sales analytics pipeline."""

from __future__ import annotations

import json

from . import analysis, visualization
from .cleaning import clean_sales
from .config import Settings, get_settings
from .data_loader import load_sales
from .kpis import compute_kpis


def run_pipeline(settings: Settings | None = None, make_figures: bool = True) -> dict:
    """Run the full analytics pipeline.

    Steps: load -> clean -> KPIs -> rankings -> RFM -> persist tables/figures.

    Returns a summary dictionary (also written to ``reports/summary.json``).
    """
    settings = settings or get_settings()
    settings.ensure_dirs()

    raw = load_sales(settings.data_file)
    df = clean_sales(raw)

    kpis = compute_kpis(df)
    monthly = analysis.monthly_sales(df)
    top_prod_sales = analysis.top_products(df, by="sales", n=10)
    top_prod_qty = analysis.top_products(df, by="quantity", n=10)
    top_cust = analysis.top_customers(df, by="sales", n=10)
    rfm = analysis.rfm_segmentation(df)

    # Persist tabular outputs as CSV for downstream BI / reporting.
    tables = {
        "monthly_sales": monthly,
        "top_products_by_sales": top_prod_sales,
        "top_products_by_quantity": top_prod_qty,
        "top_customers_by_sales": top_cust,
        "rfm_segmentation": rfm,
    }
    for name, table in tables.items():
        table.to_csv(settings.tables_dir / f"{name}.csv", index=False)

    figures: list[str] = []
    if make_figures:
        fig_dir = settings.figures_dir
        figures = [
            str(visualization.plot_monthly_sales(monthly, fig_dir)),
            str(visualization.plot_top_products(top_prod_sales, fig_dir, by="sales")),
            str(visualization.plot_category_profit(df, fig_dir)),
            str(visualization.plot_segment_distribution(rfm, fig_dir)),
        ]

    summary = {
        "dataset_rows": int(len(df)),
        "kpis": kpis.as_dict(),
        "segment_counts": rfm["segment"].value_counts().to_dict(),
        "tables": {name: str(settings.tables_dir / f"{name}.csv") for name in tables},
        "figures": figures,
    }

    with open(settings.reports_dir / "summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)

    return summary


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def print_summary(summary: dict) -> None:
    """Pretty-print the pipeline summary to stdout."""
    kpis = summary["kpis"]
    print("\n" + "=" * 60)
    print(" GLOBAL SUPERSTORE - SALES ANALYTICS SUMMARY")
    print("=" * 60)
    print(f" Records analysed     : {summary['dataset_rows']:,}")
    print(f" Date range           : {kpis['first_order_date']} -> {kpis['last_order_date']}")
    print(f" Unique orders        : {kpis['total_orders']:,}")
    print(f" Unique customers     : {kpis['total_customers']:,}")
    print(f" Total sales          : {_format_currency(kpis['total_sales'])}")
    print(f" Total profit         : {_format_currency(kpis['total_profit'])}")
    print(f" Profit margin        : {kpis['overall_profit_margin'] * 100:.2f}%")
    print(f" Avg order value      : {_format_currency(kpis['avg_order_value'])}")
    print(f" Avg discount         : {kpis['avg_discount'] * 100:.2f}%")
    print(f" Avg days to ship     : {kpis['avg_days_to_ship']:.2f}")
    print(f" Loss-making orders   : {kpis['loss_making_order_share'] * 100:.2f}%")
    print("-" * 60)
    print(" Customer segments (RFM):")
    for segment, count in summary["segment_counts"].items():
        print(f"   {segment:<18}: {count:,}")
    print("=" * 60)
    print(" Figures + tables written under: reports/")
    print("=" * 60 + "\n")
