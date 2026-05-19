import argparse
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text
from pathlib import Path

import cross


def eurovibe(chart_dir: Path, results_file: Path):
    ct = cross.build_cross_table(chart_dir, results_file)
    return ct.notna().sum(axis=1).rename("score")


def plot_scatter(merged, label_1, label_2, ax):
    sns.regplot(data=merged, x=label_1, y=label_2, ax=ax, scatter_kws={"s": 60})
    texts = [
        ax.text(row[label_1], row[label_2], country, fontsize=8)
        for country, row in merged.iterrows()
    ]
    adjust_text(texts, ax=ax, arrowprops={"arrowstyle": "-", "color": "gray", "lw": 0.5})
    ax.set_title(f"Eurovibe: {label_1} vs {label_2}")
    sns.despine(offset=5, trim=True)


def plot_slope(merged, label_1, label_2, ax):
    left_texts, right_texts = [], []

    for country, row in merged.iterrows():
        v1, v2 = row[label_1], row[label_2]
        color = "steelblue" if v2 >= v1 else "tomato"
        ax.plot([0, 1], [v1, v2], color=color, alpha=0.7, linewidth=1.5)
        ax.scatter([0, 1], [v1, v2], color=color, s=30, zorder=3)
        left_texts.append(ax.text(-0.03, v1, country, ha="right", va="center", fontsize=8))
        right_texts.append(ax.text(1.03, v2, country, ha="left", va="center", fontsize=8))

    adjust_text(left_texts, ax=ax, only_move={"text": "y"})
    adjust_text(right_texts, ax=ax, only_move={"text": "y"})

    ax.set_xticks([0, 1])
    ax.set_xticklabels([label_1, label_2], fontsize=11)
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel("Eurovibe score")
    ax.set_title(f"Eurovibe: {label_1} vs {label_2}")
    sns.despine(left=False, bottom=True, offset=5)
    ax.xaxis.set_ticks_position("none")


def plot_dumbbell(merged, label_1, label_2, ax):
    sorted_df = merged.sort_values(label_2)
    countries = sorted_df.index.tolist()
    y = range(len(countries))

    for i, (country, row) in enumerate(sorted_df.iterrows()):
        v1, v2 = row[label_1], row[label_2]
        color = "steelblue" if v2 >= v1 else "tomato"
        ax.plot([v1, v2], [i, i], color=color, linewidth=2, alpha=0.7)

    ax.scatter(sorted_df[label_1], list(y), color="gray", s=60, zorder=3, label=label_1)
    ax.scatter(sorted_df[label_2], list(y), color="steelblue", s=60, zorder=3, label=label_2)

    ax.set_yticks(list(y))
    ax.set_yticklabels(countries, fontsize=8)
    ax.set_xlabel("Eurovibe score")
    ax.set_title(f"Eurovibe: {label_1} vs {label_2}")
    ax.legend(loc="lower right")
    sns.despine(offset=5, trim=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-dir-1", required=True)
    parser.add_argument("--chart-dir-2", required=True)
    parser.add_argument("--results-1", required=True)
    parser.add_argument("--results-2", required=True)
    parser.add_argument("--label-1", default="First")
    parser.add_argument("--label-2", default="Second")
    parser.add_argument("--type", choices=["scatter", "slope", "dumbbell"], default="scatter")
    parser.add_argument("--output", default="plots/eurovibe_compare.png")
    args = parser.parse_args()

    s1 = eurovibe(Path(args.chart_dir_1), Path(args.results_1))
    s2 = eurovibe(Path(args.chart_dir_2), Path(args.results_2))

    merged = s1.rename(args.label_1).to_frame().join(
        s2.rename(args.label_2).to_frame(), how="inner"
    )

    tall = args.type in ("slope", "dumbbell")
    fig, ax = plt.subplots(figsize=(8, 9) if tall else (8, 7))

    if args.type == "slope":
        plot_slope(merged, args.label_1, args.label_2, ax)
    elif args.type == "dumbbell":
        plot_dumbbell(merged, args.label_1, args.label_2, ax)
    else:
        plot_scatter(merged, args.label_1, args.label_2, ax)

    plt.tight_layout()

    out = Path(args.output)
    out.parent.mkdir(exist_ok=True)
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
