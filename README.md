# Housing Affordability in England and Wales

An exploratory analysis of the Office for National Statistics (ONS) house-price-to-earnings ratios for local authorities, 1997–2025. The initial question is: **where has the post-2021 improvement reached, and where does buying a home remain far out of reach?**

> **Status:** Initial data review. The published visual report has not been built yet.

## Data

The workbook in `data/` is the ONS 2025 release, published 26 March 2026. It includes local-authority time series for median and lower-quartile house-price-to-earnings ratios. Sheets `5c` and `6c` contain the England and Wales local-authority series.

- [ONS source dataset](https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian)
- [ONS 2025 bulletin and methodology](https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/housingaffordabilityinenglandandwales/2025)

The ONS reports median national ratios of 7.6 for England and 6.0 for Wales in 2025. Those national ratios differ from the median of the local-authority ratios reported below.

## Initial findings

Calculated from the workbook's median local-authority ratio series (`5c`):

- The median across local authorities with data fell from **9.41 in 2021** to **8.03 in 2025**.
- **23 areas** had ratios below the ONS's broad five-times-earnings benchmark in 2025; **33 areas** had ratios of 12 or above, down from 76 in 2021.
- The 2025 range ran from **4.08 in Hyndburn** to **25.22 in Kensington and Chelsea**.
- Between 2024 and 2025, ratios fell in 213 areas, rose in 103, were unchanged in one, and were unavailable for the Isles of Scilly.

The lower-quartile series (`6c`) offers another view of lower-priced homes and lower earners. It can help test whether the apparent recovery extends to the entry-level market.

## Important interpretation limits

The ratio divides house prices by gross annual earnings for full-time employees, based on where people work. It describes individual earnings, not household income, and excludes self-employment. It does not account for joint earners, deposits, existing equity, mortgage rates or ongoing housing costs. The ONS calls five times earnings a broad affordability indicator, not a complete test of whether a household can buy.

House prices are not mix-adjusted: the type of properties sold can vary by year and area. The data cover England and Wales; a separate ONS series is needed for a UK-wide household-income measure. ONS earnings estimates also have sampling and comparability limitations, especially around 2020–2021.

## Reproduce the initial summary

```powershell
python -m pip install -r requirements.txt
python scripts/analyze.py
```

## Attribution

Contains Office for National Statistics data, reused under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). Source: *Housing affordability in England and Wales: 2025*, released 26 March 2026.
