import pandas as pd
import json
from pathlib import Path
import os


def check_country(country_file: str, results_df: pd.DataFrame):
    folder = "kworb_charts"
    country_df = pd.read_csv(folder + "/" + country_file)

    mapping_path = Path("./mapping.json")

    with mapping_path.open("r", encoding="utf-8") as f:
        mapping_names = json.load(f)

    mapping_df = pd.read_csv("./country_map.csv")
    countries_on_the_chart = pd.merge(country_df, results_df, on="Artist")[
        ["Pos", "Country", "Points", "Public", "Jury"]
    ]
    country_code = country_file.split("_")[0]
    country_name = country_code
    try:
        country_name = mapping_names[country_code]
    except KeyError:
        print(f"Code {country_code} isn't on the dict")

    if "Israel" in countries_on_the_chart["Country"].to_numpy():
        il_pos = countries_on_the_chart.loc[
            countries_on_the_chart["Country"] == "Israel", "Pos"
        ].iloc[0]
        print(f"Hooray! {country_name} loves us ({il_pos})")
        if "Sweden" in countries_on_the_chart["Country"].to_numpy():
            sw_pos = countries_on_the_chart.loc[
                countries_on_the_chart["Country"] == "Sweden", "Pos"
            ].iloc[0]
            print(f"Oh they love Sweden too ({sw_pos})")
        print()
    # else:
    #     print(f"{country_file.split('_')[0]} are anitisemites")

    return countries_on_the_chart


def main():
    results_df = pd.read_csv("./results.csv")
    for country_file in os.listdir("kworb_charts"):
        check_country(country_file, results_df)


if __name__ == "__main__":
    main()
