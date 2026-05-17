# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Multi-year Eurovision data analysis (2025 and 2026) correlating Spotify chart performance with voting results. The pipeline fetches chart data, builds cross-country comparison tables, and generates visualizations for a blog post.

## Commands

```bash
# Fetch chart snapshots (use --out-dir to avoid overwriting previous fetches)
uv run python fetch.py --out-dir kworb_charts_YYYYMMDD

# Generate charts (PNGs saved to plots/)
uv run python generate_charts.py --chart-dir kworb_charts_YYYYMMDD --suffix YYYY

# Build cross-table interactively / ad-hoc
uv run python cross.py

# Quick per-country chart check
uv run python check_all.py

# Install/sync dependencies
uv sync
```

## Data pipeline

1. **`fetch.py`** — scrapes Kworb Spotify daily charts for all countries; `--out-dir` controls output folder (default: `kworb_charts/`)
2. **`cross.py`** — builds a cross-table from a chart folder + `tables/results.csv`: rows = chart country, columns = Eurovision country, values = best chart position. Contains all plotting helpers (`plot_cross_table`, `scatter_charts_scores`, `plot_count`, etc.)
3. **`generate_charts.py`** — saves 4 PNGs (cross heatmap, scatter, bar count, eurovibe) for any year. Pass `--chart-dir` and `--suffix` to control inputs and output filenames. Optionally override `--results` and `--plots-dir`.
4. **`check_all.py`** — quick per-country check: how often and how highly a target country charted across all scraped charts

## Key files and data

- **`mapping.json`** — maps 2-letter ISO country codes to full country names
- **`tables/`** — 2026 data: `results.csv` (final scores with Place, Country, Song, Artist, Points, Public, Jury, Running)
- **`tables2025/`** — archived 2025 tables (results, jury, public, cross-tables)
- **`charts/`**, **`charts2106/`** — 2025 chart snapshots (week 1 and ~1 month later)
- **`kworb_charts_20260517/`** — 2026 chart snapshot (day after contest; re-fetch in ~2 days for richer data)
- **`plots/`** — generated PNGs (2025 originals + 2026 `*_2026.png` files)
- **`post2026.md`** — draft 2026 blog update (to be merged into the existing post on menisadi.github.io)
- **`post.qmd`** — 2025 Quarto source (renders with `quarto render post.qmd`)

## Yearly workflow

For each new snapshot: run `fetch.py --out-dir kworb_charts_YYYYMMDD`, update `CHART_FOLDER` in `generate_charts_2026.py`, re-run it. Artist matching is done on lowercased name — check for mismatches if chart counts look unexpectedly low.

## Dependencies

All declared in `pyproject.toml`: `pandas`, `requests`, `beautifulsoup4`, `lxml`, `matplotlib`, `seaborn`.
