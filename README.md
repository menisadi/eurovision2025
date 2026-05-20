# Eurovision × Spotify

Analysis correlating Eurovision Song Contest results with Spotify chart performance across national markets.

Published post: [Votes vs. Plays: Eurovision 2025 on Spotify](https://menisadi.github.io/euro25/)

## What it does

Scrapes daily national Spotify top-200 charts for all Eurovision countries, then cross-references which finalist songs appeared on each chart. Produces heatmaps, scatter plots, and a "Eurovibe" index measuring how engaged each country was with the contest.

## Setup

```bash
uv sync
```

## Pipeline

```bash
# 1. Fetch chart snapshots
uv run python fetch.py --out-dir charts/YYYYMMDD

# 2. Generate all plots (saved to plots/)
uv run python generate_charts.py --chart-dir charts/YYYYMMDD --suffix YYYY

# 3. Ad-hoc cross-table exploration
uv run python cross.py --chart-dir charts/YYYYMMDD --results tables/2026/results.csv

# 4. Quick per-country check
uv run python check_all.py --chart-dir charts/YYYYMMDD --results tables/2026/results.csv
```

## Data

- `charts/` — daily Spotify chart snapshots by date
- `tables/` — Eurovision results CSVs (2025 and 2026)
- `plots/` — generated PNG visualizations
- `mapping.json` — ISO country code → country name

## Dependencies

`pandas`, `requests`, `beautifulsoup4`, `lxml`, `matplotlib`, `seaborn`, `adjusttext`
