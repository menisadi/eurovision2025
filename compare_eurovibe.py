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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-dir-1", required=True)
    parser.add_argument("--chart-dir-2", required=True)
    parser.add_argument("--results-1", required=True)
    parser.add_argument("--results-2", required=True)
    parser.add_argument("--label-1", default="First")
    parser.add_argument("--label-2", default="Second")
    parser.add_argument("--output", default="plots/eurovibe_compare.png")
    args = parser.parse_args()

    s1 = eurovibe(Path(args.chart_dir_1), Path(args.results_1))
    s2 = eurovibe(Path(args.chart_dir_2), Path(args.results_2))

    merged = s1.rename(args.label_1).to_frame().join(
        s2.rename(args.label_2).to_frame(), how="inner"
    )

    fig, ax = plt.subplots(figsize=(8, 7))
    sns.regplot(data=merged, x=args.label_1, y=args.label_2, ax=ax, scatter_kws={"s": 60})
    texts = [
        ax.text(row[args.label_1], row[args.label_2], country, fontsize=8)
        for country, row in merged.iterrows()
    ]
    adjust_text(texts, ax=ax, arrowprops={"arrowstyle": "-", "color": "gray", "lw": 0.5})

    ax.set_title(f"Eurovibe: {args.label_1} vs {args.label_2}")
    sns.despine(offset=5, trim=True)
    plt.tight_layout()

    out = Path(args.output)
    out.parent.mkdir(exist_ok=True)
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
