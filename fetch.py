#!/usr/bin/env python3
"""
Scrape Kworb Spotify daily charts for every country and save each one as CSV.

Requires:
    pip install pandas requests beautifulsoup4 lxml
"""

import re
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.error import HTTPError

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://kworb.net/spotify/"
OUT_DIR = Path("kworb_charts")  # all CSVs end up here
OUT_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update(
    {"User-Agent": "Mozilla/5.0 (compatible; KworbChartScraper/1.0)"}
)


def get_daily_pages() -> dict[str, str]:
    """
    Parse the index page and return  {country_code: full_url_to_daily_page}.
    The “country_code” is the bit between `/country/` and `_daily.html`.
    """
    html = session.get(BASE_URL, timeout=30).text
    soup = BeautifulSoup(html, "lxml")

    pages: dict[str, str] = {}
    for a in soup.select('a[href$="_daily.html"]'):
        href = a["href"]
        href = urljoin(BASE_URL, href)  # make absolute
        m = re.search(r"/country/([^/_]+)_daily\.html", href)
        code = (
            m.group(1) if m else Path(href).stem.replace("_daily", "")
        )  # “global”
        pages[code.lower()] = href
    return pages


def scrape_chart(code: str, url: str) -> bool:
    """Download one daily chart, clean it up, and save to CSV."""
    try:
        # first (and only) table on the page is the chart
        df = pd.read_html(url, flavor="lxml")[0]
    except ValueError:
        print(f"[{code}] - no table found, skipping")
        return False
    except HTTPError:
        print(f"[{code}] - no table found, skipping")
        return False

    df.columns = [c.strip() for c in df.columns]  # tidy headers

    # Locate the Artist/Title column – sometimes it’s “Artist and Title”, sometimes “Artist & Title”
    target = next(
        (c for c in df.columns if "Artist" in c and "Title" in c), None
    )
    if target:
        split = df[target].str.split(" - ", n=1, expand=True)
        df["Artist"] = split[0]
        df["Track"] = split[1]
    else:
        print(f"[{code}] couldn’t find the Artist/Title column – kept as-is")

    out_path = OUT_DIR / f"{code}_daily.csv"
    df.to_csv(out_path, index=False)
    print(f"[{code}] → {out_path}")
    return True


def main() -> None:
    pages = get_daily_pages()
    print(f"Found {len(pages)} daily pages")
    for code, url in pages.items():
        scrape_chart(code, url)
        time.sleep(0.5)  # be polite to the server


if __name__ == "__main__":
    main()
