#!/usr/bin/env python3
"""Capture screenshots of presentation slide decks for preview images.

Requires: playwright (install via `uv pip install playwright && playwright install chromium`)
"""

import asyncio
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "public" / "images" / "presentations"

PRESENTATIONS = [
    ("second-hardest-cs-thing", "https://indrajeetpatil.github.io/second-hardest-cs-thing/"),
    ("to-comment-or-not", "https://indrajeetpatil.github.io/to-comment-or-not/"),
    ("foss-for-enterprise", "https://indrajeetpatil.github.io/foss-for-enterprise/"),
    ("parse-dont-pray", "https://indrajeetpatil.github.io/parse-dont-pray/"),
    ("dry-r-package-development", "https://indrajeetpatil.github.io/dry-r-package-development/"),
    ("preventive-r-package-care", "https://indrajeetpatil.github.io/preventive-r-package-care/"),
    ("intro-to-ggstatsplot", "https://indrajeetpatil.github.io/intro-to-ggstatsplot/"),
    ("intro-to-snapshot-testing", "https://indrajeetpatil.github.io/intro-to-snapshot-testing/"),
    ("academia-to-industry", "https://indrajeetpatil.github.io/academia-to-industry/"),
]


async def capture_screenshot(page, name: str, url: str) -> None:
    """Navigate to a presentation URL and capture a screenshot."""
    output_path = OUTPUT_DIR / f"{name}.png"
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)  # Allow animations to settle
        await page.screenshot(path=str(output_path), type="png")
        print(f"  {name}")
    except Exception as e:
        print(f"  {name} (failed: {e})")


async def main() -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright not installed. Run:")
        print("  uv pip install playwright && playwright install chromium")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Capturing presentation screenshots...")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 720})

        for name, url in PRESENTATIONS:
            await capture_screenshot(page, name, url)

        await browser.close()

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
