# Case 2 preprocessing (Walnut Creek)

## What the pipeline does

1. **`gdalwarp`** each L2 layer to **EPSG:32611** and **clip** to `walnut-creek-study-box.shp` (same as your Eaton GeoTIFF workflow).
2. **Screen pixels** (same rules as `eaton/scripts/tempo/screen_tempo_pixels.py`):
   - `main_data_quality_flag` ≤ **0** (normal only; use `--qa-main-max 1` to allow “suspicious”).
   - `eff_cloud_fraction` ≤ **0.3** (`--cloud-max`).
   - Tropospheric VCD finite / not fill.
3. **Enhancement:** `ΔVCD = VCD − median(VCD)` over **screened** pixels in the box (simple local background). For smoke you used plume fraction × ΔVCD; here we use **median background** without `f_p` unless you add it later.
4. **Mass:** `mass_kg = ΔVCD [molecules/cm²] × pixel_area [cm²] / N_A × M_NO2` → **`massno2-plant-clipped.tif`**.

## Do you need your own VCD or AMF?

- **Usually no.** TEMPO L2 already provides **`/product/vertical_column_troposphere`** (tropospheric vertical column) from the operational retrieval with AMF absorbed in that product chain.
- **Optional check:** In the Eaton repo, `vcd_check_scd_amf.py` compares **SCD / AMF** to the L2 VCD for validation. That is **diagnostic**, not required for a standard Case 2 map and statistics.
- **Recompute AMF** only if your research question is retrieval consistency / ATBD experiments—not needed to “have” a tropospheric column for the plant case.

## Command

Place your **`TEMPO_NO2_L2_*.nc`** in this folder (or pass a full path), then:

```powershell
cd "C:\Users\aeaturu\Desktop\WORK April 2026\eaton-2\casestudy2"
py -3 preprocess_tempo_walnut.py --nc "YOUR_FILE.nc"
```

Outputs include **`massno2-plant-clipped.tif`**, intermediate `walnut_tempo_*_utm11_clipped.tif`, and **`walnut_tempo_mask_screen.tif`**.

Then:

```powershell
py -3 ..\tempo_case_analysis.py massno2-plant-clipped.tif --case-id case2_plant
py -3 ..\refresh_comparison_table.py
```

## Requirements

- **GDAL** on PATH (`gdalwarp`, `gdalinfo` — same as QGIS/OSGeo4W).
- Python: `numpy`, `rasterio` (see repo `requirements.txt`).
