"""Dataset loading utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import get_settings

# Columns we expect every record to carry. Used as a lightweight schema check.
EXPECTED_COLUMNS = {
    "order_id",
    "order_date",
    "ship_date",
    "ship_mode",
    "customer_name",
    "segment",
    "state",
    "country",
    "market",
    "region",
    "product_id",
    "category",
    "sub_category",
    "product_name",
    "sales",
    "quantity",
    "discount",
    "profit",
    "shipping_cost",
    "order_priority",
    "year",
}


def load_sales(path: str | Path | None = None) -> pd.DataFrame:
    """Load the Global Superstore dataset from Excel or CSV.

    Parameters
    ----------
    path:
        Optional override for the dataset location. When omitted the path from
        :func:`sales_analysis.config.get_settings` is used.

    Returns
    -------
    pandas.DataFrame
        The raw dataset.

    Raises
    ------
    FileNotFoundError
        If the dataset file does not exist.
    ValueError
        If the file extension is not supported or required columns are missing.
    """
    data_path = Path(path) if path is not None else get_settings().data_file

    if not data_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{data_path}'. Set the SALES_DATA_FILE "
            "environment variable or pass an explicit path."
        )

    suffix = data_path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(data_path)
    elif suffix == ".csv":
        df = pd.read_csv(data_path)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Use .xlsx, .xls or .csv."
        )

    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            "Dataset is missing expected columns: " + ", ".join(sorted(missing))
        )

    return df
