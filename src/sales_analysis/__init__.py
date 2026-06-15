"""Sales Analysis - a reproducible analytics toolkit for the Global Superstore dataset.

This package turns the exploratory notebook work into a modular, testable and
reproducible pipeline. The public API exposes the most commonly used building
blocks so they can be imported directly::

    from sales_analysis import load_sales, clean_sales, compute_kpis

See :mod:`sales_analysis.pipeline` for the end-to-end orchestration and the
``sales-analysis`` command line entry point.
"""

from __future__ import annotations

from .analysis import (
    days_to_ship_distribution,
    monthly_sales,
    rfm_segmentation,
    top_customers,
    top_products,
)
from .cleaning import clean_sales
from .config import Settings, get_settings
from .data_loader import load_sales
from .kpis import compute_kpis

__all__ = [
    "Settings",
    "get_settings",
    "load_sales",
    "clean_sales",
    "compute_kpis",
    "monthly_sales",
    "top_products",
    "top_customers",
    "rfm_segmentation",
    "days_to_ship_distribution",
]

__version__ = "1.0.0"
