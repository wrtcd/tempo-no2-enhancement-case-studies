Case 1 — Eaton smoke plume
==========================
See ../METHODS_TEMPO.md for locked workflow.

- massno2-eaton-clipped.tif — clipped enhancement NO2 mass per pixel (Float32; NoData -1e30).
- eaton-study-box.* — ~9.65 km x ~9.65 km study box (~93.2 km2); clipped raster footprint ~93.22 km2 (3x3 TEMPO pixels).
- TEMPO L2 source: TEMPO_NO2_L2_V03_20250109T184504Z_S008G09.nc (granule QA percents in case1_metadata.csv).

Run metrics: py -3 ../tempo_case_analysis.py massno2-eaton-clipped.tif --case-id case1_smoke
