from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ons_housing_affordability_2025.xlsx"


def load_local_authority_ratios(sheet: str) -> pd.DataFrame:
    """Read the ONS workbook's local-authority ratio table (5c or 6c)."""
    frame = pd.read_excel(DATA, sheet_name=sheet, header=1)
    for year in ("2021", "2024", "2025"):
        frame[year] = pd.to_numeric(frame[year], errors="coerce")
    return frame


def summarize(sheet: str, label: str) -> None:
    frame = load_local_authority_ratios(sheet)
    latest = frame["2025"]
    change = frame["2025"] - frame["2024"]
    valid_change = change.dropna()

    print(f"\n{label} (sheet {sheet})")
    print(f"Rows: {len(frame)}; 2025 values: {latest.notna().sum()}")
    for year in ("2021", "2024", "2025"):
        print(f"Median local-authority ratio, {year}: {frame[year].median():.2f}")
    print(f"Below 5 in 2025: {(latest < 5).sum()}")
    print(f"At least 12 in 2025: {(latest >= 12).sum()}")
    print(f"Improved since 2024: {(valid_change < 0).sum()}")
    print(f"Worsened since 2024: {(valid_change > 0).sum()}")
    print(f"Unchanged since 2024: {(valid_change == 0).sum()}")
    print("\nLowest 2025 ratios:")
    print(frame.nsmallest(5, "2025")[["Local authority name", "2025"]].to_string(index=False))
    print("\nHighest 2025 ratios:")
    print(frame.nlargest(5, "2025")[["Local authority name", "2025"]].to_string(index=False))


if __name__ == "__main__":
    summarize("5c", "Median house price / median workplace earnings")
    summarize("6c", "Lower-quartile house price / lower-quartile workplace earnings")
