# Case 3 — Dense urban (Downtown Los Angeles)

**Status:** Implemented — same **TEMPO granule** and preprocessing rules as Case 2 for **matched meteorology**.

## Study box (`la-study-box.shp`)

- **EPSG:32611**, same **width × height** as Cases 1–2 (~**9.655 km × ~9.655 km**, ~**93.22 km²** vector area).
- **Center (WGS84):** **34.05223°N, −118.24368°W** — Downtown LA / Civic Center (adjust in QGIS if you prefer a different urban core).
- Files: `la-study-box.shp` (+ `.shx`, `.dbf`, `.prj`, `.cpg`).

## TEMPO granule (date + time)

Use the **same** Level-2 file as Case 2 so plant vs city comparisons share **one overpass**:

| Field | Value |
|--------|--------|
| **File** | `TEMPO_NO2_L2_V03_20250723T210939Z_S012G09.nc` |
| **Scene start (UTC)** | **2025-07-23T21:09:39Z** |
| **Scene end (UTC)** | **2025-07-23T21:16:16Z** |
| **Local (PDT, ~UTC−7)** | ~**14:09–14:16** on 23 Jul 2025 |

**Path:** NetCDF lives under `casestudy2/`; Case 3 preprocessing uses that path (same file on disk).

## Preprocessing

From repo root (`eaton-2`):

```powershell
py -3 casestudy2\preprocess_tempo_walnut.py
  --nc casestudy2\TEMPO_NO2_L2_V03_20250723T210939Z_S012G09.nc
  --box casestudy3\la-study-box.shp
  --out-dir casestudy3
  --prefix la_tempo
  --mass-name massno2-city-clipped.tif
```

## Analysis

```powershell
py -3 tempo_case_analysis.py casestudy3\massno2-city-clipped.tif --case-id case3_city
py -3 refresh_comparison_table.py
```

## Metadata

- [`case3_metadata.csv`](case3_metadata.csv) — full row.

See also [`../casestudy2/CASE2_PREPROCESS.md`](../casestudy2/CASE2_PREPROCESS.md) for QA/cloud rules and enhancement definition.
