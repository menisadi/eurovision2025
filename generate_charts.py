import argparse
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

import cross


def save_cross_table(cross_table, plots_dir, suffix):
    mask = cross_table.isna()
    plt.figure(figsize=(11, 9))
    sns.heatmap(
        cross_table,
        cmap="viridis_r",
        mask=mask,
        linewidths=0.5,
        annot=True,
        fmt=".0f",
        cbar_kws={"label": "Best chart position"},
    )
    plt.title("How each country ranks on every other country's chart")
    plt.tight_layout()
    plt.savefig(plots_dir / f"cross_{suffix}.png", dpi=150)
    plt.close()
    print(f"Saved cross_{suffix}.png")


def save_scatter(cross_table, results_file, plots_dir, suffix):
    merged = cross.charts_and_scores(str(results_file), cross_table)
    merged["Rank"] = len(merged) - merged["Place"] + 1

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(data=merged, x="Rank", y="Charts", ax=ax, scatter_kws={"s": 80})
    for _, row in merged.iterrows():
        ax.text(row["Rank"] + 0.3, row["Charts"] + 0.15, row["Country"], fontsize=9, va="center", ha="left")
    x_range = range(1, len(merged) + 1)
    ax.set_xticks(ticks=list(x_range), labels=list(x_range)[::-1])
    ax.set_title("Charts vs. Rank by Country")
    ax.set_xlabel("Place")
    ax.set_ylabel("Number of charts")
    ax.set_xlim(0.5, len(merged) + 0.5)
    sns.despine(offset=5, trim=True)
    plt.tight_layout()
    plt.savefig(plots_dir / f"scatter_{suffix}.png", dpi=150)
    plt.close()
    print(f"Saved scatter_{suffix}.png")


def save_vote_scatter(cross_table, results_file, plots_dir, suffix):
    merged = cross.charts_and_scores(str(results_file), cross_table)
    melted = merged.melt(
        id_vars=["Country", "Charts"],
        value_vars=["Public", "Jury"],
        var_name="Vote Type",
        value_name="Votes",
    )

    g = sns.FacetGrid(melted, col="Vote Type", height=6, aspect=0.85, sharex=False)
    g.map_dataframe(sns.regplot, x="Votes", y="Charts", scatter_kws={"s": 80})

    for ax, vote_type in zip(g.axes.flat, ["Public", "Jury"]):
        subset = melted[melted["Vote Type"] == vote_type]
        for _, row in subset.iterrows():
            ax.text(row["Votes"] + 1, row["Charts"] + 0.15, row["Country"], fontsize=8)

    g.set_axis_labels("Points", "Number of charts")
    g.set_titles(col_template="{col_name} vote vs. charts")
    g.figure.tight_layout()
    g.savefig(plots_dir / f"vote_scatter_{suffix}.png", dpi=150)
    plt.close()
    print(f"Saved vote_scatter_{suffix}.png")


def save_bar_count(cross_table, plots_dir, suffix):
    cross_table.notna().sum().sort_values(ascending=False).plot(kind="bar")
    plt.ylabel("Number of charts")
    plt.title("On how many charts each Eurovision song charted")
    plt.tight_layout()
    plt.savefig(plots_dir / f"bar_count_{suffix}.png", dpi=150)
    plt.close()
    print(f"Saved bar_count_{suffix}.png")


def save_eurovibe(cross_table, plots_dir, suffix):
    cross_table.notna().sum(axis=1).sort_values(ascending=False).plot(kind="bar")
    plt.ylabel("Number of finalist songs in top-200")
    plt.title("Eurovibe: finalist songs per country (week one)")
    plt.tight_layout()
    plt.savefig(plots_dir / f"eurovibe_bars_{suffix}.png", dpi=150)
    plt.close()
    print(f"Saved eurovibe_bars_{suffix}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-dir", required=True, help="Folder containing chart CSVs")
    parser.add_argument("--suffix", required=True, help="Suffix for output filenames (e.g. 2026)")
    parser.add_argument("--results", default="tables/results.csv", help="Results CSV (default: tables/results.csv)")
    parser.add_argument("--plots-dir", default="plots", help="Output folder for PNGs (default: plots)")
    args = parser.parse_args()

    chart_dir = Path(args.chart_dir)
    results_file = Path(args.results)
    plots_dir = Path(args.plots_dir)
    plots_dir.mkdir(exist_ok=True)

    cross_table = cross.build_cross_table(chart_dir, results_file)
    save_cross_table(cross_table, plots_dir, args.suffix)
    save_scatter(cross_table, results_file, plots_dir, args.suffix)
    save_vote_scatter(cross_table, results_file, plots_dir, args.suffix)
    save_bar_count(cross_table, plots_dir, args.suffix)
    save_eurovibe(cross_table, plots_dir, args.suffix)


if __name__ == "__main__":
    main()
