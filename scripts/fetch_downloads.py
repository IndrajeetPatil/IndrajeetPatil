#!/usr/bin/env python3
"""Fetch CRAN download counts for R packages and write to data/download_counts.json."""

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
import polars as pl

PACKAGES = [
    "ggstatsplot",
    "statsExpressions",
    "datawizard",
    "insight",
    "performance",
    "parameters",
    "effectsize",
    "correlation",
    "bayestestR",
    "modelbased",
    "report",
    "see",
    "lintr",
    "styler",
    "ggsignif",
]

CRAN_API = "https://cranlogs.r-pkg.org/downloads/total/1900-01-01:2099-12-31"
OUTPUT = Path(__file__).parent.parent / "data" / "download_counts.json"


def fetch_counts() -> pl.DataFrame:
    """Fetch all-time download counts from CRAN logs API."""
    package_str = ",".join(PACKAGES)
    response = httpx.get(f"{CRAN_API}/{package_str}", timeout=30)
    response.raise_for_status()
    return pl.DataFrame(response.json()).select("package", "downloads")


def format_count(n: int) -> str:
    """Format a number as a human-readable string (e.g., '10.1M', '745K')."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def main() -> None:
    df = fetch_counts()

    packages = {
        row["package"]: {"downloads": row["downloads"], "formatted": format_count(row["downloads"])}
        for row in df.iter_rows(named=True)
    }

    total = df["downloads"].sum()

    result = {
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
        "total": total,
        "total_formatted": format_count(total),
        "packages": packages,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Updated {OUTPUT}: total={total:,} downloads ({format_count(total)})")


if __name__ == "__main__":
    main()
