# Results summary and interpretation

This file implements the **writing / interpretation** deliverable for the three TEMPO NO₂ case studies. Numbers below come from **`comparison_table.csv`** (regenerate with `py -3 refresh_comparison_table.py` after new runs).

## Comparison table (snapshot)

| case_id | narrative | study box km² (vector) | clipped footprint km² | integrated t (valid, signed) | integrated t (positive-only) | n_valid | n_positive | granule (UTC start) |
|---------|-----------|------------------------|------------------------|------------------------------|-------------------------------|---------|------------|----------------------|
| case1_smoke | Smoke / Eaton plume | 93.216 | 93.216 | 3.594 | 3.594 | 9 | 9 | 2025-01-09T18:45:04Z |
| case2_plant | Power plant (Walnut Creek) | 93.216 | 72.511 | −0.022 | 0.042 | 7 | 3 | 2025-07-23T21:09:39Z |
| case3_city | Dense urban (LA core) | 93.216 | 72.511 | −0.037 | 0.040 | 7 | 3 | 2025-07-23T21:09:39Z |

*Exact decimals may change if you re-run analysis; trust `comparison_table.csv` as source of truth.*

## Methods contrast (for thesis / paper)

### Case 1 (smoke)

- **Granule:** `TEMPO_NO2_L2_V03_20250109T184504Z_S008G09.nc` — **9 Jan 2025**, ~18:45 UTC scene.
- **Enhancement:** From the **Eaton project pipeline** (plume-scaled ΔVCD → kg/pixel); see smoke processing notes and `casestudy1/case1_metadata.csv`. **Not** the same formula as Cases 2–3 below.

### Cases 2 and 3 (plant and city)

- **Same granule** for matched meteorology: `TEMPO_NO2_L2_V03_20250723T210939Z_S012G09.nc` — **23 Jul 2025**, ~**21:09–21:16 UTC** (~14:10 local PDT).
- **Screening:** `main_data_quality_flag` ≤ 0, `eff_cloud_fraction` ≤ 0.3, finite L2 tropospheric VCD (`casestudy2/preprocess_tempo_walnut.py`).
- **Enhancement:** ΔVCD = VCD − **median(VCD)** over **screened** pixels in the box; then kg/pixel via column × pixel area (see `CASE2_PREPROCESS.md`).

### Cross-case comparability

- **Case 1 vs Cases 2–3:** **Different dates and enhancement definitions** — compare **qualitatively** (patterns, orders of magnitude) unless you harmonize processing.
- **Case 2 vs Case 3:** **Same granule, same rules, same box size** — **direct** comparison of distributions and signed / positive-only tonnes in the two windows.

## Interpretation notes

### Signed vs positive-only integrated tonnes

- **Median background** can make **ΔVCD** (and mass) **negative** on some pixels. The **signed** sum over all valid pixels can be **slightly negative** even when the plume/city has strong **positive** enhancements elsewhere.
- Report **both**:
  - **integrated_total_tonnes_valid** (signed, net enhancement in the box), and  
  - **integrated_total_tonnes_positive_only** (mass where enhancement > 0),  
  as in `tempo_case_analysis.py` output and `case_runs.csv`.

### Small sample (3×3 cells)

- After screening, **7–9 valid pixels** is **small** for histograms — treat **maps** and **integrated totals** as primary; histograms are **illustrative**.

### Optional context (not in satellite retrieval)

- **Inventories:** EPA NEI / EIA can place **facility-scale NOₓ** in context; not the same as column mass. See `INVENTORY_CONTEXT.md`.
- **Confounders:** Fill `confounders_template.csv` if you add ERA5 wind/BLH, etc.

## Figures

Standardized copies live in **`figures/`** after running `py -3 export_results_bundle.py` from the repo root.

## Sensitivity analysis (optional)

To test robustness, repeat Cases 2–3 with a **second clear-sky granule** (different date), same boxes and rules, and compare **sign** and **order of magnitude** of positive-only tonnes—not necessarily exact match.
