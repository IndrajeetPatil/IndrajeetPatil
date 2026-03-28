#!/usr/bin/env python3
"""Fetch citation counts from Google Scholar and write to data/citation_counts.json.

Uses direct HTTP requests with browser-like headers.
Falls back to existing data if Google Scholar blocks the request.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

SCHOLAR_ID = "kBjhJPcAAAAJ"
SCHOLAR_URL = f"https://scholar.google.co.in/citations?user={SCHOLAR_ID}&hl=en&cstart=0&pagesize=100"
OUTPUT = Path(__file__).parent.parent / "data" / "citation_counts.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_scholar_page(html: str) -> dict:
    """Parse citation data from Google Scholar profile HTML."""
    # Total citations from the table (first row, second column)
    citations_match = re.search(
        r'<td class="gsc_rsb_std">(\d+)</td>', html
    )
    total_citations = int(citations_match.group(1)) if citations_match else 0

    # h-index (second row)
    indices = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
    h_index = int(indices[2]) if len(indices) > 2 else 0
    i10_index = int(indices[4]) if len(indices) > 4 else 0

    # Per-publication citations
    publications = {}
    # Pattern: title in <a class="gsc_a_at">...</a>, citations in <a class="gsc_a_ac gs_ibl">N</a>
    pub_blocks = re.findall(
        r'<a[^>]*class="gsc_a_at"[^>]*>([^<]+)</a>.*?'
        r'<a[^>]*class="gsc_a_ac gs_ibl"[^>]*>(\d*)</a>.*?'
        r'<span class="gsc_a_h gsc_a_hc gs_ibl">(\d*)</span>',
        html,
        re.DOTALL,
    )
    for title, cites, year in pub_blocks:
        title = title.strip()
        publications[title] = {
            "citations": int(cites) if cites else 0,
            "year": year.strip(),
        }

    return {
        "total_citations": total_citations,
        "h_index": h_index,
        "i10_index": i10_index,
        "publications": publications,
    }


def main() -> None:
    print("Fetching Google Scholar profile...")

    try:
        resp = httpx.get(SCHOLAR_URL, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()

        if "Please show you" in resp.text or "CAPTCHA" in resp.text.upper():
            print("  Google Scholar returned a CAPTCHA page. Using existing data.")
            sys.exit(0)

        data = parse_scholar_page(resp.text)

        if data["total_citations"] == 0 and not data["publications"]:
            print("  Could not parse citation data. Using existing data.")
            sys.exit(0)

    except (httpx.HTTPError, httpx.TimeoutException) as e:
        print(f"  Failed to fetch: {e}. Using existing data.")
        sys.exit(0)

    result = {
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
        "scholar_id": SCHOLAR_ID,
        **data,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    n_pubs = len(data["publications"])
    print(f"Updated {OUTPUT}: {data['total_citations']:,} citations, h-index={data['h_index']}, {n_pubs} publications")


if __name__ == "__main__":
    main()
