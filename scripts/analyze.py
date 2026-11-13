from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "ons_housing_affordability_2025.xlsx"
ASSETS = ROOT / "assets"
DERIVED = ROOT / "data" / "derived"
YEARS = [str(year) for year in range(1997, 2026)]

INK = "#20343a"
TEAL = "#247367"
GOLD = "#d68d38"
MUTED = "#65767a"
GRID = "#e2e9e4"


def load_table(sheet: str) -> pd.DataFrame:
    frame = pd.read_excel(WORKBOOK, sheet_name=sheet, header=1)
    frame = frame.loc[frame["Local authority name"].notna()].copy()
    for year in YEARS:
        frame[year] = pd.to_numeric(frame[year], errors="coerce")
    return frame


def style_axis(ax):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", colors=MUTED, labelsize=9, length=0, pad=7)
    ax.grid(axis="y", color=GRID, linewidth=.8)
    ax.set_axisbelow(True)


def build_trend(median: pd.DataFrame, lower: pd.DataFrame):
    series = pd.DataFrame({
        "Year": [int(year) for year in YEARS],
        "Median price / median earnings": [median[year].median() for year in YEARS],
        "Lower-quartile price / lower-quartile earnings": [lower[year].median() for year in YEARS],
        "Median areas with data": [median[year].count() for year in YEARS],
        "Lower-quartile areas with data": [lower[year].count() for year in YEARS],
    })
    series.to_csv(DERIVED / "annual_local_authority_medians.csv", index=False)
    fig, ax = plt.subplots(figsize=(10.6, 4.8), layout="constrained")
    ax.plot(series.Year, series["Median price / median earnings"], color=TEAL, lw=3, label="Median price and earnings")
    ax.plot(series.Year, series["Lower-quartile price / lower-quartile earnings"], color=GOLD, lw=2.6, label="Lower-quartile price and earnings")
    ax.axhline(5, color="#84938e", lw=1.3, ls=(0,(4,4)))
    ax.text(1997, 5.22, "5x broad indicator", color=MUTED, fontsize=9)
    ax.axvline(2021, color="#bfcac4", lw=1, ls=(0,(2,4)))
    ax.text(2021.4, 10.15, "2021 peak", color=MUTED, fontsize=9)
    ax.set_xlim(1997, 2025)
    ax.set_ylim(0, 11)
    ax.set_xticks([1997,2000,2005,2010,2015,2020,2025])
    ax.set_ylabel("Ratio: years of gross earnings", color=MUTED, fontsize=10)
    ax.set_xlabel("")
    style_axis(ax)
    ax.legend(frameon=False, loc="upper left", ncol=2, fontsize=9)
    fig.savefig(ASSETS / "affordability-trend.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return series


def build_distribution(median: pd.DataFrame):
    bands = [
        ("Under 5x", lambda values: values < 5, "#478e7b"),
        ("5x to under 8x", lambda values: (values >= 5) & (values < 8), "#a9c9b8"),
        ("8x to under 12x", lambda values: (values >= 8) & (values < 12), "#e7bd79"),
        ("12x or more", lambda values: values >= 12, "#b95f4b"),
    ]
    years = ["2021", "2025"]
    counts = [[int(test(median[year]).sum()) for _, test, _ in bands] for year in years]
    fig, ax = plt.subplots(figsize=(9.6, 3.2), layout="constrained")
    left = [0, 0]
    for index, (label, _, color) in enumerate(bands):
        values = [row[index] for row in counts]
        ax.barh(years, values, left=left, color=color, height=.5, label=label, edgecolor="white", linewidth=1)
        for y, value, start in zip(years, values, left):
            if value >= 16:
                ax.text(start + value/2, y, str(value), ha="center", va="center", color=INK, fontsize=10, fontweight="bold")
        left = [start + value for start, value in zip(left, values)]
    ax.set_xlim(0, 330)
    ax.set_xlabel("Local authorities (one area missing in each year)", color=MUTED, fontsize=9)
    ax.set_ylabel("")
    ax.xaxis.grid(True, color=GRID, linewidth=.8)
    ax.yaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(axis="both", colors=MUTED, labelsize=10, length=0, pad=8)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(.5, 1.02), ncol=2, fontsize=9)
    fig.savefig(ASSETS / "ratio-distribution.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_extremes(median: pd.DataFrame):
    latest = median[["Local authority name", "2025"]].dropna().copy()
    lowest = latest.nsmallest(5, "2025")
    highest = latest.nlargest(5, "2025")
    extremes = pd.concat([lowest, highest]).sort_values("2025")
    colors = [TEAL if value < 5 else "#b95f4b" for value in extremes["2025"]]
    fig, ax = plt.subplots(figsize=(9.6, 5.1), layout="constrained")
    bars = ax.barh(extremes["Local authority name"], extremes["2025"], color=colors, height=.66)
    ax.axvline(5, color="#84938e", lw=1.2, ls=(0,(4,4)))
    ax.set_xlim(0, 28)
    ax.set_xlabel("Ratio: median house price divided by median workplace earnings", color=MUTED, fontsize=9)
    ax.xaxis.grid(True, color=GRID, linewidth=.8)
    ax.yaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(axis="both", colors=INK, labelsize=9, length=0, pad=8)
    for bar, value in zip(bars, extremes["2025"]):
        ax.text(value + .35, bar.get_y()+bar.get_height()/2, f"{value:.2f}x", va="center", color=INK, fontsize=9, fontweight="bold")
    fig.savefig(ASSETS / "area-extremes.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    ASSETS.mkdir(exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    median = load_table("5c")
    lower = load_table("6c")
    if len(median) != 318 or len(lower) != 318:
        raise ValueError("Expected 318 local-authority rows in each ONS table.")
    if median["2025"].notna().sum() != 317 or lower["2025"].notna().sum() != 317:
        raise ValueError("The 2025 ONS tables changed coverage; review the report before rendering.")

    series = build_trend(median, lower)
    build_distribution(median)
    build_extremes(median)
    area = median[["Country/Region name", "Local authority code", "Local authority name", "2021", "2024", "2025"]].copy()
    area = area.rename(columns={"2021":"median_ratio_2021", "2024":"median_ratio_2024", "2025":"median_ratio_2025"})
    area["change_2021_2025"] = area["median_ratio_2025"] - area["median_ratio_2021"]
    area["change_2024_2025"] = area["median_ratio_2025"] - area["median_ratio_2024"]
    area = area.merge(lower[["Local authority code", "2025"]].rename(columns={"2025":"lower_quartile_ratio_2025"}), on="Local authority code", how="left", validate="one_to_one")
    area.to_csv(DERIVED / "local_authority_ratios_2025.csv", index=False)

    latest = median["2025"]
    change = median["2025"] - median["2024"]
    print(f"Local authority median ratio: {median['2021'].median():.2f} in 2021; {latest.median():.2f} in 2025.")
    print(f"2025: {int((latest < 5).sum())} below 5x; {int((latest >= 12).sum())} at least 12x; {latest.notna().sum()} areas with data.")
    print(f"2024-25: {int((change < 0).sum())} fell; {int((change > 0).sum())} rose; {int((change == 0).sum())} unchanged.")
    print(f"Trend endpoints: {series.iloc[0,1]:.2f}x in 1997 to {series.iloc[-1,1]:.2f}x in 2025.")


if __name__ == "__main__":
    main()
