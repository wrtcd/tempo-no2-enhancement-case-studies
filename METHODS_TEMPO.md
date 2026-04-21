# TEMPO NO₂ enhancement study — locked workflow

This document fixes the processing and reporting rules so Cases 1–3 (smoke, power plant, dense city) stay comparable. **Do not change** these choices across cases unless you document an exception.

## Data product

- **Source:** NASA TEMPO **Level 2** nitrogen dioxide (`TEMPO_NO2_L2`), version as stated per granule filename (e.g. `V03`).
- **Reprojection:** Analysis rasters are delivered in **projected CRS** — **WGS 84 / UTM** for the study zone (e.g. **EPSG:32611** for Southern California). Reproject during preprocessing before clipping to the study box.
- **QA:** Use the same granule-level and pixel-level QA rules for every case (e.g. main_data_quality_flag / ground_pixel_quality_flag per ATBD). Record granule QA summary fields from the NetCDF (`qa_statistics` / metadata) in each case metadata CSV.

## Enhancement variable

- **Variable:** NO₂ **enhancement mass per pixel (kg)** after **background subtraction** (tropospheric column or mass vs. your defined background). Values are **enhancement**, not raw total column mass, unless you change the definition for all cases.
- **NoData:** Pixels equal to the raster NoData value (e.g. `-1e30`) are excluded from statistics.
- **Positive mask (histograms):** Histograms of **positive** enhancement use **mass > 0 kg** so the distribution is not dominated by zero-enhancement pixels.
- **Integrated total:** Report **sum of mass over all valid (finite, non-NoData) pixels** in the clipped window as **integrated_total_kg** (tonnes = kg / 1000). Optionally also report **sum over positive-only** as **integrated_positive_kg** where useful for interpretation.

## Spatial comparison

- **Equal-area windows:** Use the **same study box width and height (km)** for Cases 1–3, centered on the smoke plume, power plant, or urban core. The **clipped raster footprint** may differ slightly from the vector polygon area because of TEMPO pixel alignment; **integrated mass** uses the **raster pixels** (see `tempo_case_analysis.py` for footprint area in km²).

## Case 1 — locked (Eaton smoke plume)

These values are the **authoritative** Case 1 definition for cross-case comparison. They match [`casestudy1/case1_metadata.csv`](casestudy1/case1_metadata.csv).

| Item | Value |
|------|--------|
| Narrative | Smoke / plume NO₂ enhancement mass per pixel |
| TEMPO L2 granule | `TEMPO_NO2_L2_V03_20250109T184504Z_S008G09.nc` |
| Scene time (UTC) | 2025-01-09T18:45:04Z – 2025-01-09T18:51:41Z |
| CRS | EPSG:32611 (WGS 84 / UTM zone 11N) |
| Study box (vector) | ~9.655 km × ~9.655 km; area ~93.22 km² |
| Clipped raster | 3 × 3 TEMPO cells; pixel ~3218 m; footprint ~93.22 km² |
| Window center (approx.) | 118.629°W, 34.044°N |
| Sample size caveat | **n = 9 pixels** — use distributions with care; emphasize integrated mass + maps |

Re-run `tempo_case_analysis.py` on `casestudy1/massno2-eaton-clipped.tif` after any reclip; refresh `results/comparison_table.csv`.

## Cases 2–3 — locked (Walnut Creek plant, Los Angeles urban)

Cases **2** and **3** use the **same TEMPO granule** and the **same preprocessing** (`casestudy2/preprocess_tempo_walnut.py`: QA ≤ 0, `eff_cloud_fraction` ≤ 0.3, official L2 tropospheric VCD). **Enhancement** is **ΔVCD = VCD − median(VCD)** over screened pixels in the box, then conversion to **kg per pixel**. This differs from **Case 1** (smoke pipeline with plume weighting).

| Item | Case 2 (plant) | Case 3 (city) |
|------|----------------|----------------|
| Granule | `TEMPO_NO2_L2_V03_20250723T210939Z_S012G09.nc` | *same* |
| Scene UTC | 2025-07-23T21:09:39Z – 2025-07-23T21:16:16Z | *same* |
| Study box | `casestudy2/walnut-creek-study-box.shp` | `casestudy3/la-study-box.shp` |
| Center (approx.) | 34.0087°N, −117.9449°W | 34.05223°N, −118.24368°W |
| Mass raster | `casestudy2/massno2-plant-clipped.tif` | `casestudy3/massno2-city-clipped.tif` |
| Metadata | `casestudy2/case2_metadata.csv` | `casestudy3/case3_metadata.csv` |

**Reporting:** For median background, report **signed** integrated tonnes and **positive-only** integrated tonnes (see `results/RESULTS_AND_INTERPRETATION.md`).

## Benchmark note (~30 t)

- Any **~30 tonne** (or similar) **regional** total is an **integrated total over a very large domain** and serves as a **reference magnitude** only. It is **not** directly comparable to tonnes integrated over a **small study box** (~93 km² here) without explicit scaling discussion. Per-case **integrated tonnes over the analysis window** are the apples-to-apples cross-case numbers (same window width/height rule).

## Optional context (not required for pipeline)

- **Confounders** (wind, BLH, season, weekday): add to metadata when available for discussion.
- **EPA NEI / EIA / inventories:** optional order-of-magnitude context for named facilities; not the same observable as column enhancement mass.

## Per-case metadata

- Each case folder contains `caseN_metadata.csv` (one row) with granule id, times, CRS, study box area, clipped footprint, QA fields, and paths to clipped raster and study box vector.

## Automation in this repo

- `tempo_case_analysis.py` — metrics, histogram PNG, map PNG, append `results/case_runs.csv`.
- `refresh_comparison_table.py` — rebuild `results/comparison_table.csv` from latest `case_runs.csv` rows and granule times from `casestudy1/case1_metadata.csv`, `casestudy2/case2_metadata.csv`, `casestudy3/case3_metadata.csv`.
- `export_results_bundle.py` — copy figures and `comparison_table.csv` into `results/figures/` for submission.

## Further documentation

- [`results/RESULTS_AND_INTERPRETATION.md`](results/RESULTS_AND_INTERPRETATION.md) — methods contrast, interpretation, optional sensitivity note.
- [`MANIFEST.md`](MANIFEST.md) — data file locations.
- [`INVENTORY_CONTEXT.md`](INVENTORY_CONTEXT.md) — optional NEI/EIA disclaimer text.
- [`results/confounders_template.csv`](results/confounders_template.csv) — optional wind/BLH fields.
