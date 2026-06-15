"""Central configuration for the sales analytics pipeline.

Paths are resolved relative to the project root so the project is fully
portable - no machine specific absolute paths (unlike the original notebook
which hard-coded a Windows path).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# project_root/src/sales_analysis/config.py -> project_root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the pipeline.

    Every path can be overridden through an environment variable so the
    pipeline can be wired into CI or a container without code changes.
    """

    project_root: Path = PROJECT_ROOT
    data_file: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "SALES_DATA_FILE",
                str(PROJECT_ROOT / "superstore_sales.xlsx"),
            )
        )
    )
    reports_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("SALES_REPORTS_DIR", str(PROJECT_ROOT / "reports"))
        )
    )

    @property
    def figures_dir(self) -> Path:
        return self.reports_dir / "figures"

    @property
    def tables_dir(self) -> Path:
        return self.reports_dir / "tables"

    def ensure_dirs(self) -> None:
        """Create the output directories if they do not already exist."""
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
