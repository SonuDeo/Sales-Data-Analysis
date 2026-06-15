# Sales Data Analysis — Global Superstore

[![CI](https://github.com/SonuDeo/Sales-Data-Analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/SonuDeo/Sales-Data-Analysis/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An end-to-end, **reproducible analytics project** built on the Global Superstore
dataset (51,290 transactions across four years, seven markets and three product
categories). The project goes beyond a one-off exploratory notebook: it ships a
**modular Python package**, a **command-line pipeline**, **automated tests**, and
a **Power BI dashboard** so the same analysis can be re-run, extended, and
trusted in CI.

---

## Table of Contents

- [Highlights](#highlights)
- [Key Findings](#key-findings)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Analytics Modules](#analytics-modules)
- [Outputs](#outputs)
- [Testing & Quality](#testing--quality)
- [Roadmap](#roadmap)

---

## Highlights

- **Reproducible pipeline** — one command (`sales-analysis`) loads, cleans,
  analyses, and exports KPIs, ranked tables, and charts.
- **Modular, testable code** — a `src/` layout package with single-responsibility
  modules instead of a monolithic notebook.
- **Advanced analytics** — RFM customer segmentation, month-over-month growth,
  profitability and fulfilment-speed analysis on top of classic EDA.
- **Portable** — no hard-coded paths; the dataset location is configurable via an
  environment variable or CLI flag, and figures render on a headless backend.
- **Quality gates** — `pytest` unit tests, `ruff` linting, `black` formatting, and
  a GitHub Actions matrix build across Python 3.10–3.12.
- **Business intelligence** — a companion Power BI dashboard (`superstore dashboard.pbix`).

## Key Findings

Generated directly by the pipeline (`reports/summary.json`):

| Metric | Value |
| --- | --- |
| Records analysed | 51,290 |
| Date range | 2011-01-01 → 2014-12-31 |
| Unique orders | 25,035 |
| Unique customers | 795 |
| Total sales | $12,642,501.91 |
| Total profit | $1,469,034.82 |
| Overall profit margin | 11.62% |
| Average order value | $504.99 |
| Average discount | 14.29% |
| Average days to ship | 3.97 |
| Loss-making line items | 24.46% |

**Customer segmentation (RFM):** Champions (158) and Loyal Customers (116) form
the high-value core, while At-Risk (51) and Lost (65) cohorts are clear re-engagement
targets. Roughly a quarter of all line items are unprofitable — largely driven by
heavy discounting — making discount policy the single biggest margin lever.

> Numbers are produced reproducibly; re-running the pipeline regenerates them.

## Dataset

`superstore_sales.xlsx` — 51,290 rows × 21 columns.

| Column | Type | Description |
| --- | --- | --- |
| `order_id` | string | Unique order identifier (orders can span multiple line items) |
| `order_date`, `ship_date` | datetime | Order and shipment dates |
| `ship_mode` | string | Shipping method |
| `customer_name`, `segment` | string | Customer and business segment |
| `state`, `country`, `market`, `region` | string | Geography |
| `product_id`, `category`, `sub_category`, `product_name` | string | Product hierarchy |
| `sales`, `profit`, `shipping_cost`, `discount` | float | Financial measures |
| `quantity` | int | Units ordered |
| `order_priority` | string | Order priority |
| `year` | int | Order year |

## Project Structure

```
Sales-Data-Analysis/
├── src/sales_analysis/        # Python package
│   ├── config.py              # Environment-overridable paths & settings
│   ├── data_loader.py         # Excel/CSV loading + schema validation
│   ├── cleaning.py            # Deduplication + feature engineering
│   ├── kpis.py                # Headline business KPIs
│   ├── analysis.py            # Trends, rankings, RFM segmentation
│   ├── visualization.py       # Headless Matplotlib/Seaborn charts
│   ├── pipeline.py            # End-to-end orchestration
│   └── cli.py                 # `sales-analysis` command line entry point
├── tests/                     # pytest unit tests
├── reports/                   # Generated tables, figures, summary.json (gitignored)
├── Sales Analysis.ipynb       # Original exploratory notebook
├── superstore dashboard.pbix  # Power BI dashboard
├── superstore_sales.xlsx      # Source dataset
├── pyproject.toml             # Packaging, console script & tooling config
├── requirements*.txt          # Runtime / dev dependencies
└── .github/workflows/ci.yml   # Lint + test matrix (3.10–3.12)
```

## Architecture

```
        superstore_sales.xlsx
                 │
          data_loader.load_sales          (read + schema check)
                 │
          cleaning.clean_sales            (dedup, dates, derived features)
                 │
      ┌──────────┼───────────────┐
      ▼          ▼               ▼
  kpis.compute  analysis.*    visualization.*
   _kpis       (trends, RFM,   (charts → PNG)
                rankings)
      └──────────┼───────────────┘
                 ▼
          pipeline.run_pipeline
                 │
        reports/  (summary.json · tables/*.csv · figures/*.png)
```

## Quickstart

```bash
# 1. Clone
git clone https://github.com/SonuDeo/Sales-Data-Analysis.git
cd Sales-Data-Analysis

# 2. Create an environment & install (editable, with dev extras)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 3. Run the full analytics pipeline
sales-analysis
```

## Usage

**Command line**

```bash
sales-analysis                  # full pipeline + figures, prints a summary
sales-analysis --no-figures     # KPIs + CSV tables only (fast)
sales-analysis --data my.csv    # analyse a custom .xlsx/.xls/.csv dataset
sales-analysis --quiet          # suppress stdout summary
```

**As a library**

```python
from sales_analysis import load_sales, clean_sales, compute_kpis
from sales_analysis.analysis import rfm_segmentation, monthly_sales

df = clean_sales(load_sales())

kpis = compute_kpis(df)
print(kpis.total_sales, kpis.overall_profit_margin)

trend = monthly_sales(df)          # monthly sales/profit + MoM growth
segments = rfm_segmentation(df)    # one row per customer with an RFM segment
```

The dataset path can also be set without touching code:

```bash
export SALES_DATA_FILE=/path/to/superstore_sales.xlsx
export SALES_REPORTS_DIR=/path/to/output
```

## Analytics Modules

| Module | Responsibility |
| --- | --- |
| `data_loader` | Loads `.xlsx`/`.xls`/`.csv`, validates the expected schema |
| `cleaning` | Removes duplicates, coerces dates, derives `days_to_ship`, `profit_margin`, `month_year`, `is_profitable` |
| `kpis` | Computes a typed `SalesKPIs` dataclass (sales, profit, margin, AOV, fulfilment, loss share) |
| `analysis` | Monthly trends with MoM growth, top products/customers, days-to-ship distribution, **RFM segmentation** |
| `visualization` | Saves trend, top-products, sub-category profit, and RFM-segment charts as PNGs |
| `pipeline` | Wires everything together and persists results |

## Outputs

Running the pipeline writes to `reports/` (gitignored):

- `reports/summary.json` — machine-readable KPIs and segment counts
- `reports/tables/*.csv` — monthly sales, top products/customers, RFM table
- `reports/figures/*.png` — monthly trend, top products, sub-category profit, RFM segments

## Testing & Quality

```bash
pytest -q             # run the unit-test suite
ruff check src tests  # lint
black src tests       # format
```

Continuous integration runs the lint and test suite on every push and pull
request across Python 3.10, 3.11, and 3.12.

## Roadmap

- Time-series forecasting of monthly sales (e.g. Prophet / statsmodels)
- Cohort and retention analysis
- An interactive Streamlit dashboard alongside the Power BI report
- Data-quality contract checks (e.g. Great Expectations / pandera)

---

## License

Released under the MIT License. See [LICENSE](LICENSE).
