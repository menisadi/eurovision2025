import pandas as pd
import numpy as np
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


def charts_and_scores(final_path: str, cross_df: pd.DataFrame):
    final = final = pd.read_csv(final_path)
    counts = cross_df.notna().sum().sort_values(ascending=False)
    counts.name = "Charts"

    merged = pd.merge(left=counts, right=final, left_index=True, right_on="Country")

    return merged


def final_tables(table_path):
    table_df = pd.read_csv(table_path)
    table_df = table_df.drop(columns=["Unnamed: 0", "Total"])
    table_df = table_df.set_index("Country")

    return table_df


def plot_cross_table(cross, label, title, reverse=False):
    mask = cross.isna()

    plt.figure(figsize=(11, 9))
    pallete = "viridis_r" if reverse else "viridis"

    sns.heatmap(
        cross,
        cmap=pallete,
        mask=mask,  # hide NaNs
        linewidths=0.5,
        annot=True,
        fmt=".0f",  # numbers inside cells (optional)
        cbar_kws={"label": label},
    )

    plt.title(title)
    plt.tight_layout()
    plt.show()


def compare2(charts, jury, public):
    not_in_final = [c for c in jury.columns if c not in jury.index]
    jury = jury.drop(columns=not_in_final)
    public = public.drop(columns=not_in_final)

    charts = charts.sort_index().sort_index(axis=1)
    jury = jury.reindex_like(charts)
    public = public.reindex_like(charts)

    charts_vec = charts.to_numpy().ravel()  # 1-D array of length n_rows * n_cols
    jury_vec = jury.to_numpy().ravel()
    public_vec = public.to_numpy().ravel()

    flat_df = pd.DataFrame(
        {
            "charts": charts_vec,
            "jury": jury_vec,
            "public": public_vec,
        }
    )

    pearson_corr = flat_df.corr(method="pearson")
    spearman_corr = flat_df.corr(method="spearman")

    print("Pearson")
    print(pearson_corr)
    print("Spearman")
    print(spearman_corr)


def compare(charts, jury, public):
    not_in_final = [c for c in jury.columns if c not in jury.index]
    jury = jury.drop(columns=not_in_final)
    public = public.drop(columns=not_in_final)

    charts = charts.sort_index().sort_index(axis=1)
    jury = jury.reindex_like(charts)
    public = public.reindex_like(charts)

    charts_df = charts.stack()  # a pd.Series indexed by (row_index, col_index)
    jury_df = jury.stack()
    public_df = public.stack()

    df = pd.concat(
        [
            charts_df.rename("Charts"),
            jury_df.rename("Jury"),
            public_df.rename("Public"),
        ],
        axis=1,
    )

    corr_matrix = df.corr()
    print(corr_matrix)

    # sns.heatmap(corr_matrix)
    # pd.plotting.scatter_matrix(df, diagonal="kde", figsize=(6, 6))
    # plt.tight_layout()
    # plt.show()


def plot_heats(cross_table, jury_table, public_table):
    plot_cross_table(
        cross_table,
        label="Best chart position",
        title="How each country ranks on every other country's chart",
        reverse=True,
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


def scatter_charts_scores(merged_tables):
    merged_tables["Rank"] = len(merged_tables) - merged_tables["Place"] + 1
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(
        data=merged_tables,
        x="Rank",
        y="Charts",
        s=80,  # marker size
        ax=ax,
    )

    # --- add country labels next to each point ---
    for _, row in merged_tables.iterrows():
        ax.text(
            row["Rank"] + 0.3,
            row["Charts"] + 0.3,
            row["Country"],
            fontsize=9,
            va="center",
            ha="left",
        )

    # --- tidy up ---
    x_range = range(1, len(merged_tables) + 1)
    ax.set_xticks(ticks=x_range, labels=x_range[::-1])
    ax.xticks = range(len(merged_tables) + 1, 1, -1)
    ax.set_title("Charts vs. Rank by Country")
    ax.set_xlabel("Rank")
    ax.set_ylabel("Charts")
    sns.despine(
        offset=5, trim=True
    )  # removes top/right spines; comment out if you want the full box
    plt.tight_layout()
    plt.show()


def plot_count(cross):
    cross.notna().sum().sort_values(ascending=False).plot(kind="bar")

    plt.ylabel("Number of charts")
    plt.title("On how many charts each Eurovision song charted")
    # plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main() -> None:
    cross_table = build_cross_table()
    # cross_table.to_csv("cross_first.csv")

    # jury_table = final_tables("./jury.csv")
    # public_table = final_tables("./public.csv")

    # compare(cross_table, jury_table, public_table)
    # compare2(cross_table, jury_table, public_table)
    # plot_heats(cross_table, jury_table, public_table)
    # plot_count(cross_table)

    # scores_and_charts = charts_and_scores("./results.csv", cross_table)
    # scatter_charts_scores(scores_and_charts)


if __name__ == "__main__":
    main()
