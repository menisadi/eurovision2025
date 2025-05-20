import pandas as pd
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

CHART_FOLDER = Path("kworb_charts")
RESULTS_FILE = Path("results.csv")
MAPPING_FILE = Path("mapping.json")


def load_country_mapping(mapping_path: Path = MAPPING_FILE) -> dict:
    with mapping_path.open(encoding="utf-8") as f:
        return json.load(f)


def build_cross_table(
    chart_folder: Path = CHART_FOLDER, results_file: Path = RESULTS_FILE
) -> pd.DataFrame:
    """
    Return a DataFrame whose (row, col) entry holds the position that *col-country*
    reaches in the chart owned by *row-country*. Missing → 0.
    """
    results_df = pd.read_csv(results_file)[["Artist", "Country"]].drop_duplicates()
    mapping = load_country_mapping()

    long_records = []  # will collect rows: ChartCountry, Country, Pos

    for chart_path in chart_folder.glob("*.csv"):
        country_code = chart_path.stem.split("_")[0]
        chart_country = mapping.get(country_code, country_code)

        chart_df = pd.read_csv(chart_path)[["Artist", "Pos"]]
        merged = (
            chart_df.merge(results_df, on="Artist", how="inner")
            .assign(ChartCountry=chart_country)
            .loc[:, ["ChartCountry", "Country", "Pos"]]
        )

        long_records.append(merged)

    long_df = pd.concat(long_records, ignore_index=True)

    cross = (
        long_df.pivot_table(
            index="ChartCountry",
            columns="Country",
            values="Pos",
            aggfunc="min",
            fill_value=0,
        )
        .astype(int)
        .sort_index()
        .sort_index(axis=1)
    )
    return cross


def main() -> None:
    cross_table = build_cross_table()

    # Pretty print to console
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(cross_table)

    # …and/or save:
    cross_table.to_csv("country_cross_table.csv")
    print("\nSaved → country_cross_table.csv")


if __name__ == "__main__":
    main()
