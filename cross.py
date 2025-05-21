import pandas as pd
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

CHART_FOLDER = Path("charts")
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
    results_df["artist_lower"] = results_df["Artist"].str.lower()
    mapping = load_country_mapping()

    long_records = []  # will collect rows: ChartCountry, Country, Pos

    for chart_path in chart_folder.glob("*.csv"):
        country_code = chart_path.stem.split("_")[0]
        chart_country = mapping.get(country_code, country_code)

        chart_df = pd.read_csv(chart_path)[["Artist", "Pos"]]
        chart_df["artist_lower"] = chart_df["Artist"].str.lower()
        merged = (
            chart_df.merge(results_df, on="artist_lower", how="inner")
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
        )
        .sort_index()
        .sort_index(axis=1)
    )
    return cross


def final_points_table(table_path):
    table_df = pd.read_csv(table_path)
    table_df = table_df.drop(columns=["Unnamed: 0", "Total"])
    table_df = table_df.set_index("Country")

    return table_df


def plot_cross_table(cross, label, title):
    mask = cross.isna()

    plt.figure(figsize=(11, 9))

    sns.heatmap(
        cross,
        cmap="viridis_r",  # _r reverses so dark = low rank (better)
        mask=mask,  # hide NaNs
        linewidths=0.5,
        annot=True,
        fmt=".0f",  # numbers inside cells (optional)
        cbar_kws={"label": label},
    )

    plt.title(title)
    plt.tight_layout()
    plt.show()


def main() -> None:
    cross_table = build_cross_table()

    jury_table = final_points_table("./jury.csv")
    public_table = final_points_table("./public.csv")

    plot_cross_table(
        cross_table,
        label="Best chart position",
        title="How each country ranks on every other country's chart",
    )
    plot_cross_table(
        public_table,
        label="Points",
        title="How many points each country gave",
    )
    plot_cross_table(
        jury_table,
        label="Points",
        title="How many points each jury gave",
    )


if __name__ == "__main__":
    main()
