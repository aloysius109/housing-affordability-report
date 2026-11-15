# The affordability squeeze

A data-led report on house-price-to-workplace-earnings ratios across local authorities in England and Wales, 1997-2025.

The report focuses on two questions: how far has affordability improved since the 2021 peak, and how many local areas remain above the ONS's broad five-times-earnings indicator.

It includes a local-authority explorer, a banded map of 2025 ratios, and downloadable derived data. A standalone Medium-edition article and four chart images are in `medium-edition/`.

## Published report

The report is designed for GitHub Pages at https://aloysius109.github.io/housing-affordability-report/.

## Data source

- [ONS House price to workplace-based earnings ratio dataset](https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian)
- [ONS Housing affordability in England and Wales: 2025](https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/housingaffordabilityinenglandandwales/2025)

The workbook in `data/` is the ONS 2025 release, published 26 March 2026. It contains median and lower-quartile local-authority series for England and Wales. The report uses tables 5c and 6c.

## Rebuild

```powershell
python -m pip install -r requirements.txt
python scripts/analyze.py
quarto render
```

The analysis script writes SVG charts to `assets/` and derived CSV/JSON files to `data/derived/`. Quarto renders the report to `_site/index.html`. Run `python scripts/analyze.py --medium` to also export the four article charts as 200-dpi PNGs in `medium-edition/images/`.

The map uses the vendored, ultra-generalised ONS local-authority boundaries in `data/geo/local_authorities.geojson`; routine builds do not need a network connection. To refresh the boundary file from the ONS ArcGIS service, run `python scripts/fetch_boundaries.py` and review any code changes before publishing. The GitHub Actions `Report checks` workflow rebuilds the report assets and verifies the headline figures, derived data, area-code coverage and download links. Run it locally with `python scripts/check_report.py` after `python scripts/analyze.py`.

## Source watch

`sources/watch.json` records the ONS 2025 release this report was built from: the fingerprint of the workbook served at the dataset's `current` address, which is byte-identical to the vendored copy in `data/`, and the absence of a 2026 bulletin. Run `python scripts/check_sources.py` to compare that baseline with ONS today; the script only reads upstream, and never changes the report.

The **Source watch** workflow runs the same check every Monday and opens an issue labelled `source-watch` when the workbook changes, the 2026 bulletin appears, or a source cannot be read. One open issue is kept at a time, so an unadopted release does not reopen weekly. GitHub disables scheduled workflows after 60 days without repository activity; if this report sits untouched for two months, dispatch the workflow manually to re-enable it.

Adopting a new release is a deliberate edit, not an automatic one: replace the workbook in `data/`, re-run `scripts/analyze.py`, update every figure quoted in `index.qmd`, re-run `scripts/check_report.py`, then re-baseline the watcher with `python scripts/check_sources.py --update`.

## Interpretation

The ratio is house price divided by gross annual workplace-based earnings for full-time employees. It is an individual earnings comparison, not household income, and does not include deposits, existing equity, mortgage rates, joint earners or ongoing housing costs. The ONS describes five times earnings as a broad affordability indicator, not a complete test of whether someone can buy.

The national England and Wales ratios in the ONS bulletin are calculated from country-level values. They should not be confused with the median of local-authority ratios calculated in this report.

## Attribution

Contains Office for National Statistics data, reused under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Analytics

The report uses GoatCounter, configured in `analytics.html`. Update the `data-goatcounter` URL in that partial if the account changes. It is used without cookies, a consent banner or personal-data collection.
