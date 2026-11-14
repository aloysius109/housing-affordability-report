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

## Interpretation

The ratio is house price divided by gross annual workplace-based earnings for full-time employees. It is an individual earnings comparison, not household income, and does not include deposits, existing equity, mortgage rates, joint earners or ongoing housing costs. The ONS describes five times earnings as a broad affordability indicator, not a complete test of whether someone can buy.

The national England and Wales ratios in the ONS bulletin are calculated from country-level values. They should not be confused with the median of local-authority ratios calculated in this report.

## Attribution

Contains Office for National Statistics data, reused under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
