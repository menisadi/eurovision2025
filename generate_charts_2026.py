import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path

import cross

CHART_FOLDER = Path("kworb_charts_20260517")
RESULTS_FILE = Path("tables/results.csv")
PLOTS_DIR = Path("plots")


def save_cross_table():
    cross_table = cross.build_cross_table(CHART_FOLDER, RESULTS_FILE)

    mask = cross_table.isna()
    plt.figure(figsize=(11, 9))
    import seaborn as sns
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
    plt.savefig(PLOTS_DIR / "cross_2026.png", dpi=150)
    plt.close()
    print("Saved cross_2026.png")

    return cross_table


def save_scatter(cross_table):
    merged = cross.charts_and_scores(str(RESULTS_FILE), cross_table)
    merged["Rank"] = len(merged) - merged["Place"] + 1

    fig, ax = plt.subplots(figsize=(8, 6))
    import seaborn as sns
    sns.scatterplot(data=merged, x="Rank", y="Charts", s=80, ax=ax)
    for _, row in merged.iterrows():
        ax.text(row["Rank"] + 0.3, row["Charts"] + 0.3, row["Country"], fontsize=9, va="center", ha="left")
    x_range = range(1, len(merged) + 1)
    ax.set_xticks(ticks=list(x_range), labels=list(x_range)[::-1])
    ax.set_title("Charts vs. Rank by Country")
    ax.set_xlabel("Rank")
    ax.set_ylabel("Charts")
    sns.despine(offset=5, trim=True)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "scatter_2026.png", dpi=150)
    plt.close()
    print("Saved scatter_2026.png")


def save_bar_count(cross_table):
    cross_table.notna().sum().sort_values(ascending=False).plot(kind="bar")
    plt.ylabel("Number of charts")
    plt.title("On how many charts each Eurovision song charted")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "bar_count_2026.png", dpi=150)
    plt.close()
    print("Saved bar_count_2026.png")


def save_eurovibe(cross_table):
    cross_table.notna().sum(axis=1).sort_values(ascending=False).plot(kind="bar")
    plt.ylabel("Number of finalist songs in top-200")
    plt.title("Eurovibe: finalist songs per country (week one)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "eurovibe_bars_2026.png", dpi=150)
    plt.close()
    print("Saved eurovibe_bars_2026.png")


def main():
    PLOTS_DIR.mkdir(exist_ok=True)
    cross_table = save_cross_table()
    save_scatter(cross_table)
    save_bar_count(cross_table)
    save_eurovibe(cross_table)


if __name__ == "__main__":
    main()
