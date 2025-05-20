import pandas as pd
import json
from pathlib import Path
import os


def check_country(
    country_file: str, results_df: pd.DataFrame, target_country: str
) -> int:
    folder = "kworb_charts"
    country_df = pd.read_csv(folder + "/" + country_file)

    mapping_path = Path("./mapping.json")

    with mapping_path.open("r", encoding="utf-8") as f:
        mapping_names = json.load(f)

    countries_on_the_chart = pd.merge(country_df, results_df, on="Artist")[
        ["Pos", "Country", "Points", "Public", "Jury"]
    ]
    country_code = country_file.split("_")[0]
    country_name = country_code
    try:
        country_name = mapping_names[country_code]
    except KeyError:
        print(f"Code {country_code} isn't on the dict")

    if target_country in countries_on_the_chart["Country"].to_numpy():
        il_pos = countries_on_the_chart.loc[
            countries_on_the_chart["Country"] == target_country, "Pos"
        ].iloc[0]

        return il_pos

    else:
        return 0


def main():
    results_df = pd.read_csv("./results.csv")

    # target_country = "Israel"
    target_country = "Estonia"
    files_list = os.listdir("kworb_charts")
    posistions = [
        check_country(country_file, results_df, target_country)
        for country_file in files_list
    ]

    print(f"Country: {target_country}")
    print(round(sum(posistions) / len(posistions), 2))
    print(round(len([p for p in posistions if p > 0]) / len(files_list), 2))


if __name__ == "__main__":
    main()
