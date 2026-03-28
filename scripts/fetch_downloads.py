#!/usr/bin/env python3
"""Fetch CRAN download counts, PyPI download counts, and GitHub stars, then write to data/download_counts.json."""

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
import polars as pl

R_PACKAGES = [
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

PYPI_PACKAGES = [
    "crosszip",
]

# (owner, repo) tuples for all packages
GITHUB_REPOS = {
    "ggstatsplot": ("IndrajeetPatil", "ggstatsplot"),
    "statsExpressions": ("IndrajeetPatil", "statsExpressions"),
    "datawizard": ("easystats", "datawizard"),
    "insight": ("easystats", "insight"),
    "performance": ("easystats", "performance"),
    "parameters": ("easystats", "parameters"),
    "effectsize": ("easystats", "effectsize"),
    "correlation": ("easystats", "correlation"),
    "bayestestR": ("easystats", "bayestestR"),
    "modelbased": ("easystats", "modelbased"),
    "report": ("easystats", "report"),
    "see": ("easystats", "see"),
    "lintr": ("r-lib", "lintr"),
    "styler": ("r-lib", "styler"),
    "ggsignif": ("const-ae", "ggsignif"),
    "crosszip": ("IndrajeetPatil", "crosszip"),
}

CRAN_API = "https://cranlogs.r-pkg.org/downloads/total/1900-01-01:2099-12-31"
OUTPUT = Path(__file__).parent.parent / "data" / "download_counts.json"


def format_count(n: int) -> str:
    """Format a number as a human-readable string (e.g., '10.1M', '745K')."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def fetch_cran_downloads(client: httpx.Client) -> dict[str, int]:
    """Fetch all-time download counts from CRAN logs API."""
    package_str = ",".join(R_PACKAGES)
    response = client.get(f"{CRAN_API}/{package_str}", timeout=30)
    response.raise_for_status()
    df = pl.DataFrame(response.json()).select("package", "downloads")
    return {row["package"]: row["downloads"] for row in df.iter_rows(named=True)}


def fetch_pypi_downloads(client: httpx.Client) -> dict[str, int]:
    """Fetch recent download counts from PyPI Stats API."""
    downloads = {}
    for pkg in PYPI_PACKAGES:
        try:
            resp = client.get(
                f"https://pypistats.org/api/packages/{pkg}/overall",
                headers={"Accept": "application/json"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                total = sum(row.get("downloads", 0) for row in data if row.get("category") == "without_mirrors")
                downloads[pkg] = total
            else:
                print(f"  Warning: PyPI Stats API returned {resp.status_code} for {pkg}")
                downloads[pkg] = 0
        except httpx.HTTPError as e:
            print(f"  Warning: Failed to fetch PyPI downloads for {pkg}: {e}")
            downloads[pkg] = 0
    return downloads


def fetch_github_stars(client: httpx.Client) -> dict[str, int]:
    """Fetch star counts from GitHub API for all repos."""
    stars = {}
    for pkg, (owner, repo) in GITHUB_REPOS.items():
        try:
            resp = client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10,
            )
            if resp.status_code == 200:
                stars[pkg] = resp.json().get("stargazers_count", 0)
            else:
                print(f"  Warning: GitHub API returned {resp.status_code} for {owner}/{repo}")
                stars[pkg] = 0
        except httpx.HTTPError as e:
            print(f"  Warning: Failed to fetch stars for {owner}/{repo}: {e}")
            stars[pkg] = 0
    return stars


def main() -> None:
    with httpx.Client() as client:
        print("Fetching CRAN download counts...")
        cran_downloads = fetch_cran_downloads(client)

        print("Fetching PyPI download counts...")
        pypi_downloads = fetch_pypi_downloads(client)

        print("Fetching GitHub stars...")
        stars = fetch_github_stars(client)

    # Merge all downloads
    all_downloads = {**cran_downloads, **pypi_downloads}

    # Build per-package data
    packages: dict[str, dict] = {}
    for pkg in [*R_PACKAGES, *PYPI_PACKAGES]:
        entry: dict = {"stars": stars.get(pkg, 0)}
        if pkg in all_downloads:
            entry["downloads"] = all_downloads[pkg]
            entry["downloads_formatted"] = format_count(all_downloads[pkg])
        packages[pkg] = entry

    total_downloads = sum(all_downloads.values())

    result = {
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
        "total_downloads": total_downloads,
        "total_downloads_formatted": format_count(total_downloads),
        "packages": packages,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Updated {OUTPUT}: total={total_downloads:,} downloads ({format_count(total_downloads)})")


if __name__ == "__main__":
    main()
