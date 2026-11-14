import json
import re
from pathlib import Path

import pandas as pd

from analyze import YEARS, load_table

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message: str):
    if not condition:
        raise AssertionError(message)


def main():
    report_path = ROOT / "index.qmd"
    report = report_path.read_text(encoding="utf-8")
    median = load_table("5c")
    lower = load_table("6c")
    latest = median["2025"]
    change = latest - median["2024"]
    distribution_2021 = median["2021"]

    require(len(median) == 318 and len(lower) == 318, "Expected 318 rows in each source table.")
    require(round(median["2025"].median(), 2) == 8.03, "2025 median no longer matches the report headline.")
    require(round(median["2021"].median(), 2) == 9.41, "2021 peak no longer matches the report headline.")
    require(round((median["2025"].median() / median["2021"].median() - 1) * 100) == -15,
            "The percentage change since 2021 no longer rounds to -15%.")
    require(int((latest > 5).sum()) == 294 and latest.notna().sum() == 317,
            "The count above five times earnings or available 2025 coverage changed.")
    require(int((change > 0).sum()) == 103 and int((change < 0).sum()) == 213 and int((change == 0).sum()) == 1,
            "The 2024–25 rise/fall/unchanged counts changed.")
    require(int((distribution_2021 >= 12).sum()) == 76 and int((latest >= 12).sum()) == 33,
            "The 12x-or-more distribution counts changed.")
    require(int((distribution_2021 < 5).sum()) == 10 and int((latest < 5).sum()) == 23,
            "The under-5x distribution counts changed.")
    lowest = median.loc[median["2025"].idxmin()]
    highest = median.loc[median["2025"].idxmax()]
    require(lowest["Local authority name"] == "Hyndburn" and round(lowest["2025"], 2) == 4.08,
            "The lowest-area headline changed.")
    require(highest["Local authority name"] == "Kensington and Chelsea" and round(highest["2025"], 2) == 25.22,
            "The highest-area headline changed.")

    claims = [
        "8.03x", "9.41x", "-15%", "294 of 317", '<span class="metric">103</span>',
        "Local authorities where the ratio rose in 2025",
        "213 fell; 1 was unchanged; 1 had no 2025 value", "76 in 2021 to 33 in 2025",
        "below 5x rose from 10 to 23", "4.08x in Hyndburn", "25.22x in Kensington and Chelsea",
        "317 available area values", "133 from five to under eight", "128 from eight to under twelve",
    ]
    for claim in claims:
        require(claim in report, f"Expected report claim is missing or changed: {claim}")

    annual = pd.read_csv(ROOT / "data" / "derived" / "annual_local_authority_medians.csv")
    area = pd.read_csv(ROOT / "data" / "derived" / "local_authority_ratios_2025.csv", dtype={"Local authority code": str})
    history = json.loads((ROOT / "data" / "derived" / "local_authority_history.json").read_text(encoding="utf-8"))
    require(annual["Year"].tolist() == [int(year) for year in YEARS], "Annual median CSV has an unexpected year range.")
    require(len(area) == 318 and area["Local authority code"].is_unique, "Area ratio CSV has the wrong row count or duplicate codes.")
    require(history.get("years") == [int(year) for year in YEARS], "Explorer JSON has an unexpected year range.")
    history_areas = history.get("areas", [])
    report_codes = set(area["Local authority code"])
    require(len(history_areas) == 318, "Explorer JSON has the wrong number of areas.")
    require({item.get("code") for item in history_areas} == report_codes, "Explorer JSON area codes do not match the ratio CSV.")
    expected_years = set(YEARS)
    for item in history_areas:
        require(set(item.get("median", {})) == expected_years, f"Unexpected median history schema for {item.get('code')}.")
        require(set(item.get("lower_quartile", {})) == expected_years,
                f"Unexpected lower-quartile history schema for {item.get('code')}.")

    geojson = json.loads((ROOT / "data" / "geo" / "local_authorities.geojson").read_text(encoding="utf-8"))
    boundary_codes = [feature.get("properties", {}).get("code") for feature in geojson.get("features", [])]
    require(len(boundary_codes) == 318 and len(set(boundary_codes)) == 318, "Boundary GeoJSON has missing or duplicate codes.")
    require(set(boundary_codes) == report_codes, "Boundary GeoJSON codes do not match the report area codes.")

    download_section = report.split("## Download the data", 1)
    require(len(download_section) == 2, "Download section is missing.")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", download_section[1])
    require(len(links) == 4, "Expected four reader-facing data download links.")
    for link in links:
        require((ROOT / link).is_file(), f"Download target does not exist: {link}")

    print("Report QA passed: headline figures, derived data, area boundaries, and all four download targets are consistent.")


if __name__ == "__main__":
    main()