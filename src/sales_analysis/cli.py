"""Command line interface for the sales analytics pipeline.

Usage::

    sales-analysis                 # run full pipeline + figures
    sales-analysis --no-figures    # skip plotting
    sales-analysis --data path.csv # use a custom dataset
"""

from __future__ import annotations

import argparse
import os
import sys

from .pipeline import print_summary, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sales-analysis",
        description="Run the Global Superstore sales analytics pipeline.",
    )
    parser.add_argument(
        "--data",
        help="Path to the dataset (.xlsx/.xls/.csv). Defaults to the bundled file.",
    )
    parser.add_argument(
        "--no-figures",
        action="store_true",
        help="Skip figure generation (tables + KPIs only).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Do not print the summary to stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.data:
        os.environ["SALES_DATA_FILE"] = args.data

    # Import after the env var is set so settings pick up the override.
    from .config import get_settings

    get_settings.cache_clear()  # type: ignore[attr-defined]

    try:
        summary = run_pipeline(make_figures=not args.no_figures)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print_summary(summary)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
