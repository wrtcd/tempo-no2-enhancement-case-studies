# TEMPO NO₂ enhancement case studies — detailed write-up

This document summarizes what was built for the three TEMPO Level-2 NO₂ **enhancement** case studies, **when** each observation applies (year, date, UTC and Pacific local time), how results were computed, and how to reproduce the **3×3** comparison (three cases × three VCD/mass pathways).

**Repository:** [wrtcd/tempo-no2-enhancement-case-studies](https://github.com/wrtcd/tempo-no2-enhancement-case-studies)

---

## 1. Time, year, and date for each case

All scenes use TEMPO **L2 v03** products. **Year is 2025** for all three cases. Local times below use `America/Los_Angeles` (PST in January, PDT in July).

### Case 1 — Eaton smoke plume (January 2025)

| Field | Value |
|--------|--------|
| **Narrative** | Smoke / plume NO₂ enhancement (Eaton area, Southern California). |
| **Calendar date (UTC, scene start)** | **2025-01-09** |
| **Scene interval (UTC)** | **18:45:04 – 18:51:41** |
| **Pacific local** | **10:45 – 10:51 PST** (Thursday, **winter**). |
| **Granule** | `TEMPO_NO2_L2_V03_20250109T184504Z_S008G09.nc` |
| **L2 file production (UTC)** | 2025-01-10T00:03:28Z |

**Framing:** This is a **single wintertime** overpass, mid-morning local, capturing smoke-related enhancement in a fixed ~9.65 km × 9.65 km box (see `casestudy1/case1_metadata.csv`). It is **not** the same calendar day or season as Cases 2–3.

### Cases 2 and 3 — July 2025, same granule

| Field | Case 2 (Walnut Creek / plant) | Case 3 (LA dense urban) |
|--------|--------------------------------|-------------------------|
| **Calendar date (scene start, UTC)** | **2025-07-23** | **2025-07-23** (same) |
| **Scene interval (UTC)** | **21:09:39 – 21:16:16** | **21:09:39 – 21:16:16** (same) |
| **Pacific local** | **14:09 – 14:16 PDT** (Wednesday, **summer** afternoon) | Same |
| **Granule** | `TEMPO_NO2_L2_V03_20250723T210939Z_S012G09.nc` | Same |
| **L2 file production (UTC)** | 2025-07-24T01:45:22Z | Same |

**Framing:** Cases 2 and 3 are **strictly time-aligned**: identical granule, identical preprocessing rules, and the **same** screened pixels for median background, but **different** study vectors (`walnut-creek-study-box.shp` vs `la-study-box.shp`) over the same ~9.65 km window size. That supports **direct** comparison of plant vs urban core in the same meteorological and illumination context (within a ~7 minute scan window).

A machine-readable summary lives in `results/case_study_time_context.csv`.

---

## 2. What we did (end-to-end)

1. **Defined three case studies** with locked spatial rules: equal study-box width/height in km (see `METHODS_TEMPO.md`), UTM 11N (EPSG:32611) for analysis rasters, and per-case centering (smoke, named power-plant box, downtown LA).
2. **Ingested TEMPO L2 NO₂** with documented QA: granule file names, UTC start/end, and QA summary percentages are recorded in `casestudy1/case1_metadata.csv`, `casestudy2/case2_metadata.csv`, and `casestudy3/case3_metadata.csv`.
3. **Case 1 (smoke)** used enhancement mass per pixel from the **Eaton / plume pipeline** (plume-scaled Δ column → kg per pixel, background removed per that workflow). This definition **differs** from the median-ΔVCD approach used in Cases 2–3.
4. **Cases 2–3 (plant, city)** used `preprocess_tempo_walnut.py`–style screening: `main_data_quality_flag` ≤ 0, `eff_cloud_fraction` ≤ 0.3, finite L2 tropospheric VCD, then **ΔVCD = VCD − median(VCD)** over **screened** pixels in the box, then column-to-mass per pixel. Metadata points to the clipped rasters and notes on signed vs positive-only mass.
5. **Aggregation and reporting:** `tempo_case_analysis.py` integrates mass over the clipped window, reports footprint area, **signed** and **positive-only** totals (tonnes), and optional min/median/max over all valid pixels. Histograms (positive mass only) are diagnostic for small 3×3 cell counts.
6. **3×3 matrix (cases × VCD pathway):** We compared three ways of defining the column / mass path—**operational** (L2 as used in the branch pipeline), **vcd_check** (SCD/L2-AMF “check” pathway), and **vcd_adj** (AMF adjustment via the `eaton-vcd-adj` workflow where applicable). The driver is `scripts/generate_3x3_matrix.py`, which clips Case 1 masses from the companion `no2-plume-vcd-branches` `outputs/08_mass` when present, and runs `scripts/case23_mass_three_vcd.py` for Cases 2–3 (GDAL and dependencies as documented). Outputs: `results/comparison_table_3x3.csv`, `results/case_runs_3x3.csv`, and per-pathway GeoTIFFs and histograms under `casestudy1/`, `casestudy2/`, `casestudy3/`.

---

## 3. Results snapshot (3×3, fixed run)

The following integrated totals (tonnes) come from `results/comparison_table_3x3.csv` (analysis run on **2026-04-27** in UTC as recorded in `case_runs_3x3.csv`). Rounding is as in the CSV.

| Case | Pathway | Integrated t (valid, signed) | Integrated t (positive-only) |
|------|---------|-----------------------------|------------------------------|
| Smoke (1) | operational | 3.524 | 3.524 |
| Smoke (1) | vcd_check | 3.594 | 3.594 |
| Smoke (1) | vcd_adj | 0.661 | 0.661 |
| Plant (2) | operational | −0.022 | 0.042 |
| Plant (2) | vcd_check | 0.0015 | 0.0725 |
| Plant (2) | vcd_adj | −0.020 | 0.0185 |
| City (3) | operational | −0.037 | 0.040 |
| City (3) | vcd_check | 0.028 | 0.090 |
| City (3) | vcd_adj | −0.0455 | 0.0098 |

**Interpretation (brief):** Case 1 shows **order-one tonne** positive-only totals in the box across pathways, with **vcd_adj** much lower than operational / vcd_check (pathway sensitivity). Cases 2–3 often have **signed** sums near zero or slightly negative (median background on mixed pixels) while **positive-only** mass remains a useful magnitude for the enhanced subset—consistent with `results/RESULTS_AND_INTERPRETATION.md`. **Do not** compare Case 1 tonnes directly to 2–3 as “the same” physical experiment: different **dates, seasons, and enhancement definitions**; compare Case 1 qualitatively or after harmonized processing.

---

## 4. Reproduction

- **Environment:** Python 3 with `requirements.txt`; Cases 2–3 three-pathway mass may require GDAL on `PATH` and the `eaton-vcd-adj` adjacency for `vcd_adj` (see `scripts/case23_mass_three_vcd.py` and `scripts/generate_3x3_matrix.py` headers).
- **Regenerate 3×3 table:** from repository root, `py -3 scripts/generate_3x3_matrix.py`. The default parent for finding `no2-plume-vcd-branches/outputs/08_mass` and related paths is `WORK April 2026\geometric corrections` unless you set `TEMPO_CASE_WORK` to another directory.
- **Single-raster analysis:** `py -3 tempo_case_analysis.py --help` (use `--runs-csv` to append to a chosen runs file).

---

## 5. Files to cite for time and methods

- `results/case_study_time_context.csv` — one row per case: year, dates, UTC and Pacific local ranges, granule, season.
- `METHODS_TEMPO.md` — locked workflow.
- `results/RESULTS_AND_INTERPRETATION.md` — signed vs positive-only, cross-case comparability.
- `MANIFEST.md` — data paths and script index.

This write-up, the time-context CSV, and the 3×3 results tables together document **what** was done and **when** each case applies in calendar and solar time.
