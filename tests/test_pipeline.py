"""Unit tests for the sales analytics pipeline using a small synthetic dataset."""

from __future__ import annotations

import pandas as pd
import pytest

from sales_analysis.analysis import (
    monthly_sales,
    rfm_segmentation,
    top_customers,
    top_products,
)
from sales_analysis.cleaning import clean_sales
from sales_analysis.kpis import compute_kpis


@pytest.fixture()
def raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["A-1", "A-1", "B-2", "C-3", "C-3"],
            "order_date": pd.to_datetime(
                ["2013-01-01", "2013-01-01", "2013-02-15", "2014-03-10", "2014-03-10"]
            ),
            "ship_date": pd.to_datetime(
                ["2013-01-04", "2013-01-04", "2013-02-18", "2014-03-12", "2014-03-12"]
            ),
            "ship_mode": ["Standard"] * 5,
            "customer_name": ["Alice", "Alice", "Bob", "Cara", "Cara"],
            "segment": ["Consumer"] * 5,
            "state": ["CA", "CA", "NY", "TX", "TX"],
            "country": ["US"] * 5,
            "market": ["US"] * 5,
            "region": ["West", "West", "East", "Central", "Central"],
            "product_id": ["P1", "P2", "P1", "P3", "P2"],
            "category": ["Furniture", "Office", "Furniture", "Tech", "Office"],
            "sub_category": ["Chairs", "Paper", "Chairs", "Phones", "Paper"],
            "product_name": ["Chair", "Paper", "Chair", "Phone", "Paper"],
            "sales": [100.0, 50.0, 200.0, 300.0, 25.0],
            "quantity": [1, 2, 3, 1, 1],
            "discount": [0.0, 0.1, 0.0, 0.2, 0.0],
            "profit": [20.0, -5.0, 60.0, 90.0, 5.0],
            "shipping_cost": [5.0, 2.0, 8.0, 10.0, 1.0],
            "order_priority": ["Medium"] * 5,
            "year": [2013, 2013, 2013, 2014, 2014],
        }
    )


def test_clean_adds_derived_columns(raw_df: pd.DataFrame) -> None:
    cleaned = clean_sales(raw_df)
    for col in ("month_year", "days_to_ship", "profit_margin", "is_profitable"):
        assert col in cleaned.columns
    # No rows should be dropped (no exact duplicates here).
    assert len(cleaned) == len(raw_df)
    assert cleaned["days_to_ship"].tolist() == [3, 3, 3, 2, 2]


def test_clean_is_non_mutating(raw_df: pd.DataFrame) -> None:
    before = raw_df.copy()
    clean_sales(raw_df)
    pd.testing.assert_frame_equal(raw_df, before)


def test_kpis(raw_df: pd.DataFrame) -> None:
    kpis = compute_kpis(clean_sales(raw_df))
    assert kpis.total_records == 5
    assert kpis.total_orders == 3  # A-1, B-2, C-3
    assert kpis.total_customers == 3
    assert kpis.total_sales == pytest.approx(675.0)
    assert kpis.total_profit == pytest.approx(170.0)
    # One of five line items has negative profit.
    assert kpis.loss_making_order_share == pytest.approx(0.2)


def test_monthly_sales_sorted(raw_df: pd.DataFrame) -> None:
    monthly = monthly_sales(clean_sales(raw_df))
    assert list(monthly["month_year"]) == sorted(monthly["month_year"])
    assert {"sales", "profit", "orders", "sales_mom_growth"} <= set(monthly.columns)


def test_top_products_and_customers(raw_df: pd.DataFrame) -> None:
    cleaned = clean_sales(raw_df)
    prods = top_products(cleaned, by="sales", n=2)
    assert len(prods) == 2
    # Chair: 100 + 200 = 300 sales -> top.
    assert prods.iloc[0]["product_name"] == "Chair"

    custs = top_customers(cleaned, by="sales", n=1)
    assert custs.iloc[0]["customer_name"] == "Cara"  # 300 + 25 = 325


def test_top_products_invalid_metric(raw_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        top_products(clean_sales(raw_df), by="invalid")


def test_rfm_segmentation_shape(raw_df: pd.DataFrame) -> None:
    rfm = rfm_segmentation(clean_sales(raw_df))
    assert {"recency", "frequency", "monetary", "RFM_score", "segment"} <= set(
        rfm.columns
    )
    assert len(rfm) == 3  # three unique customers
